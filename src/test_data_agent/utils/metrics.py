"""Prometheus metrics collection."""

from prometheus_client import Counter, Histogram

# Define metrics
testdata_requests_total = Counter(
    "testdata_requests_total",
    "Total number of test data generation requests",
    ["path", "domain", "entity", "status"],
)

testdata_generation_duration_seconds = Histogram(
    "testdata_generation_duration_seconds",
    "Time spent generating test data",
    ["path"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

testdata_records_generated = Counter(
    "testdata_records_generated",
    "Total number of test data records generated",
    ["domain", "entity"],
)

testdata_validation_errors_total = Counter(
    "testdata_validation_errors_total",
    "Total number of validation errors",
    ["domain", "entity"],
)

testdata_cache_hits_total = Counter(
    "testdata_cache_hits_total",
    "Total number of cache hits",
)

testdata_coherence_score = Histogram(
    "testdata_coherence_score",
    "Coherence score of generated data",
    ["domain"],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
)


class MetricsCollector:
    """Collector for test data generation metrics."""

    @staticmethod
    def record_request(
        path: str,
        domain: str,
        entity: str,
        status: str,
        duration: float,
    ) -> None:
        """
        Record a generation request.

        Args:
            path: Generation path (traditional, llm, rag, hybrid)
            domain: Domain (ecommerce, etc.)
            entity: Entity type (cart, order, etc.)
            status: Status (success, error)
            duration: Duration in seconds
        """
        testdata_requests_total.labels(
            path=path,
            domain=domain,
            entity=entity,
            status=status,
        ).inc()

        testdata_generation_duration_seconds.labels(path=path).observe(duration)

    @staticmethod
    def record_records_generated(domain: str, entity: str, count: int) -> None:
        """
        Record generated records count.

        Args:
            domain: Domain
            entity: Entity type
            count: Number of records generated
        """
        testdata_records_generated.labels(domain=domain, entity=entity).inc(count)

    @staticmethod
    def record_validation_error(domain: str, entity: str) -> None:
        """
        Record a validation error.

        Args:
            domain: Domain
            entity: Entity type
        """
        testdata_validation_errors_total.labels(domain=domain, entity=entity).inc()

    @staticmethod
    def record_cache_hit() -> None:
        """Record a cache hit."""
        testdata_cache_hits_total.inc()

    @staticmethod
    def record_coherence_score(domain: str, score: float) -> None:
        """
        Record coherence score.

        Args:
            domain: Domain
            score: Coherence score (0.0 to 1.0)
        """
        testdata_coherence_score.labels(domain=domain).observe(score)
