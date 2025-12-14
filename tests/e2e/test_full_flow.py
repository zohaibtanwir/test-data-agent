"""End-to-end tests covering full workflows."""

import asyncio
import json

import grpc
import pytest

from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc


@pytest.fixture
def grpc_channel():
    """Create gRPC channel to running service."""
    channel = grpc.aio.insecure_channel("localhost:9091")
    yield channel
    asyncio.run(channel.close())


@pytest.fixture
def grpc_stub(grpc_channel):
    """Create gRPC stub."""
    return test_data_pb2_grpc.TestDataServiceStub(grpc_channel)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_traditional_cart_generation(grpc_stub):
    """Test end-to-end traditional cart generation."""
    request = test_data_pb2.GenerateRequest(
        request_id="e2e-traditional-cart",
        domain="ecommerce",
        entity="cart",
        count=10,
    )

    response = await grpc_stub.GenerateData(request)

    assert response.success is True
    assert response.record_count == 10
    assert response.metadata.generation_path in ["traditional", "llm"]

    # Verify data is valid JSON
    data = json.loads(response.data)
    assert len(data) == 10
    assert all("cart_id" in record for record in data)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_schemas(grpc_stub):
    """Test getting available schemas."""
    request = test_data_pb2.GetSchemasRequest(domain="ecommerce")

    response = await grpc_stub.GetSchemas(request)

    assert len(response.schemas) >= 6  # We have 6 predefined schemas
    schema_names = {schema.name for schema in response.schemas}
    assert "cart" in schema_names
    assert "order" in schema_names
    assert "product" in schema_names


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_streaming_generation(grpc_stub):
    """Test streaming large request."""
    request = test_data_pb2.GenerateRequest(
        request_id="e2e-stream-large",
        domain="ecommerce",
        entity="user",
        count=100,
    )

    chunks = []
    total_records = 0

    async for chunk in grpc_stub.GenerateDataStream(request):
        chunks.append(chunk)
        if not chunk.is_final and chunk.data:
            data = json.loads(chunk.data)
            total_records += len(data)

    # Verify we got multiple chunks
    assert len(chunks) > 1

    # Verify final chunk
    assert chunks[-1].is_final is True

    # Verify chunk indices are sequential
    for i, chunk in enumerate(chunks[:-1]):  # Exclude final chunk
        assert chunk.chunk_index == i

    # Verify we got all records
    assert total_records == 100


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_health_check(grpc_stub):
    """Test health check RPC."""
    request = test_data_pb2.HealthCheckRequest()

    response = await grpc_stub.HealthCheck(request)

    assert response.status == "healthy"
    assert "grpc_server" in response.components
    assert response.components["grpc_server"] == "operational"


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_error_handling_invalid_count(grpc_stub):
    """Test error handling for invalid count."""
    request = test_data_pb2.GenerateRequest(
        request_id="e2e-invalid-count",
        domain="ecommerce",
        entity="cart",
        count=10000,  # Exceeds max_sync_records
    )

    response = await grpc_stub.GenerateData(request)

    assert response.success is False
    assert "exceeds max sync limit" in response.error.lower()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_multiple_entities(grpc_stub):
    """Test generation for multiple entity types."""
    entities = ["cart", "order", "payment", "product", "review", "user"]
    results = []

    for entity in entities:
        request = test_data_pb2.GenerateRequest(
            request_id=f"e2e-multi-{entity}",
            domain="ecommerce",
            entity=entity,
            count=5,
        )

        response = await grpc_stub.GenerateData(request)
        results.append((entity, response.success, response.record_count))

    # All should succeed
    assert all(success for _, success, _ in results)

    # All should return correct count
    assert all(count == 5 for _, _, count in results)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_concurrent_requests(grpc_stub):
    """Test handling concurrent requests."""

    async def make_request(entity: str, count: int) -> bool:
        request = test_data_pb2.GenerateRequest(
            request_id=f"e2e-concurrent-{entity}",
            domain="ecommerce",
            entity=entity,
            count=count,
        )
        response = await grpc_stub.GenerateData(request)
        return response.success

    # Make 10 concurrent requests
    tasks = [make_request("cart", 5) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # All should succeed
    assert all(results)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_data_quality(grpc_stub):
    """Test data quality and coherence."""
    request = test_data_pb2.GenerateRequest(
        request_id="e2e-quality-check",
        domain="ecommerce",
        entity="cart",
        count=5,
        hints=["coherent", "realistic"],
    )

    response = await grpc_stub.GenerateData(request)

    assert response.success is True

    data = json.loads(response.data)

    # Check all records have required fields
    for record in data:
        assert "cart_id" in record
        assert "customer_id" in record
        assert "items" in record
        assert "total" in record

    # Check metadata includes coherence score if applicable
    if response.metadata.coherence_score > 0:
        assert response.metadata.coherence_score >= 0.0
        assert response.metadata.coherence_score <= 1.0
