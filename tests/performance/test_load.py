"""Performance/load testing for Test Data Agent."""

import asyncio
import time
from statistics import mean, median
from typing import List

import grpc

from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc


class PerformanceMetrics:
    """Collect and analyze performance metrics."""

    def __init__(self):
        self.latencies: List[float] = []
        self.errors: List[str] = []
        self.success_count = 0
        self.total_records = 0

    def record_success(self, latency: float, record_count: int):
        """Record successful request."""
        self.latencies.append(latency)
        self.success_count += 1
        self.total_records += record_count

    def record_error(self, error: str):
        """Record failed request."""
        self.errors.append(error)

    def get_percentile(self, percentile: float) -> float:
        """Calculate latency percentile."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * percentile / 100)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def summary(self) -> dict:
        """Get performance summary."""
        total_requests = self.success_count + len(self.errors)
        return {
            "total_requests": total_requests,
            "successful": self.success_count,
            "failed": len(self.errors),
            "error_rate": len(self.errors) / total_requests if total_requests > 0 else 0,
            "total_records": self.total_records,
            "latency_ms": {
                "min": min(self.latencies) * 1000 if self.latencies else 0,
                "max": max(self.latencies) * 1000 if self.latencies else 0,
                "mean": mean(self.latencies) * 1000 if self.latencies else 0,
                "median": median(self.latencies) * 1000 if self.latencies else 0,
                "p95": self.get_percentile(95) * 1000,
                "p99": self.get_percentile(99) * 1000,
            },
            "throughput_rps": self.success_count / sum(self.latencies) if self.latencies else 0,
        }


async def run_single_request(
    stub: test_data_pb2_grpc.TestDataServiceStub,
    domain: str,
    entity: str,
    count: int,
    request_id: str,
) -> tuple[float, int, str | None]:
    """
    Run a single request and measure latency.

    Returns:
        (latency, record_count, error)
    """
    try:
        start = time.time()
        response = await stub.GenerateData(
            test_data_pb2.GenerateRequest(
                request_id=request_id,
                domain=domain,
                entity=entity,
                count=count,
            )
        )
        latency = time.time() - start

        if response.success:
            return latency, response.record_count, None
        else:
            return latency, 0, response.error

    except Exception as e:
        return 0, 0, str(e)


async def scenario_traditional_simple(
    host: str = "localhost:9091", concurrency: int = 100, requests_per_client: int = 10
):
    """
    Scenario 1: Traditional generation (simple, fast).

    Target: p99 < 200ms
    """
    print("\n=== Scenario 1: Traditional Generation (Simple) ===")
    print(f"Concurrency: {concurrency}, Requests per client: {requests_per_client}")

    metrics = PerformanceMetrics()

    async def client_task(client_id: int):
        channel = grpc.aio.insecure_channel(host)
        stub = test_data_pb2_grpc.TestDataServiceStub(channel)

        for req_num in range(requests_per_client):
            request_id = f"perf-traditional-{client_id}-{req_num}"
            latency, record_count, error = await run_single_request(
                stub, "ecommerce", "user", 10, request_id
            )

            if error:
                metrics.record_error(error)
            else:
                metrics.record_success(latency, record_count)

        await channel.close()

    # Run concurrent clients
    start = time.time()
    await asyncio.gather(*[client_task(i) for i in range(concurrency)])
    total_time = time.time() - start

    # Print results
    summary = metrics.summary()
    print("\nResults:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Requests: {summary['total_requests']}")
    print(f"  Success rate: {(1 - summary['error_rate']) * 100:.1f}%")
    print(f"  Total records: {summary['total_records']}")
    print("\nLatency (ms):")
    print(f"  Min: {summary['latency_ms']['min']:.1f}")
    print(f"  Mean: {summary['latency_ms']['mean']:.1f}")
    print(f"  Median: {summary['latency_ms']['median']:.1f}")
    print(f"  p95: {summary['latency_ms']['p95']:.1f}")
    print(f"  p99: {summary['latency_ms']['p99']:.1f}")
    print(f"  Max: {summary['latency_ms']['max']:.1f}")
    print(f"\nThroughput: {summary['throughput_rps']:.1f} req/s")

    # Check target
    target_p99 = 200
    actual_p99 = summary["latency_ms"]["p99"]
    status = "✅ PASS" if actual_p99 < target_p99 else "❌ FAIL"
    print(f"\nTarget p99 < {target_p99}ms: {actual_p99:.1f}ms {status}")

    return summary


async def scenario_streaming_large(
    host: str = "localhost:9091", concurrency: int = 5, records_per_request: int = 500
):
    """
    Scenario 2: Streaming (large requests).

    Target: First chunk < 1s
    """
    print("\n=== Scenario 2: Streaming Generation (Large) ===")
    print(f"Concurrency: {concurrency}, Records per request: {records_per_request}")

    first_chunk_latencies = []
    total_latencies = []
    errors = []

    async def stream_client(client_id: int):
        channel = grpc.aio.insecure_channel(host)
        stub = test_data_pb2_grpc.TestDataServiceStub(channel)

        request_id = f"perf-stream-{client_id}"
        request = test_data_pb2.GenerateRequest(
            request_id=request_id,
            domain="ecommerce",
            entity="cart",
            count=records_per_request,
        )

        try:
            start = time.time()
            first_chunk_time = None
            chunk_count = 0

            async for chunk in stub.GenerateDataStream(request):
                if first_chunk_time is None:
                    first_chunk_time = time.time() - start
                    first_chunk_latencies.append(first_chunk_time)

                chunk_count += 1
                if chunk.is_final:
                    break

            total_time = time.time() - start
            total_latencies.append(total_time)

        except Exception as e:
            errors.append(str(e))

        await channel.close()

    # Run concurrent clients
    start = time.time()
    await asyncio.gather(*[stream_client(i) for i in range(concurrency)])
    total_time = time.time() - start

    # Print results
    print("\nResults:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Requests: {concurrency}")
    print(f"  Success rate: {((concurrency - len(errors)) / concurrency) * 100:.1f}%")

    if first_chunk_latencies:
        print("\nFirst chunk latency (ms):")
        print(f"  Min: {min(first_chunk_latencies) * 1000:.1f}")
        print(f"  Mean: {mean(first_chunk_latencies) * 1000:.1f}")
        print(f"  Max: {max(first_chunk_latencies) * 1000:.1f}")

    if total_latencies:
        print("\nTotal latency (s):")
        print(f"  Min: {min(total_latencies):.2f}")
        print(f"  Mean: {mean(total_latencies):.2f}")
        print(f"  Max: {max(total_latencies):.2f}")

    # Check target
    target_first_chunk = 1.0
    actual_first_chunk = max(first_chunk_latencies) if first_chunk_latencies else 999
    status = "✅ PASS" if actual_first_chunk < target_first_chunk else "❌ FAIL"
    print(f"\nTarget first chunk < {target_first_chunk}s: {actual_first_chunk:.2f}s {status}")


async def run_all_scenarios(host: str = "localhost:9091"):
    """Run all performance test scenarios."""
    print("╔════════════════════════════════════════════════╗")
    print("║   Test Data Agent - Performance Test Suite    ║")
    print("╚════════════════════════════════════════════════╝")
    print(f"\nTarget: {host}")

    # Scenario 1: Traditional simple (fast path)
    await scenario_traditional_simple(host, concurrency=100, requests_per_client=10)

    # Scenario 2: Streaming large
    await scenario_streaming_large(host, concurrency=5, records_per_request=500)

    print("\n" + "=" * 60)
    print("Performance testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
