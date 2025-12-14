"""OpenTelemetry tracing setup and utilities."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient, GrpcInstrumentorServer
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)

# Global tracer
_tracer: trace.Tracer | None = None


def setup_tracing(settings: Settings) -> None:
    """
    Setup OpenTelemetry tracing.

    Args:
        settings: Application settings
    """
    global _tracer

    if not settings.tracing_enabled:
        logger.info("tracing_disabled")
        return

    try:
        # Create resource
        resource = Resource(attributes={SERVICE_NAME: settings.service_name})

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Create OTLP exporter
        otlp_exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)

        # Add batch span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument gRPC
        GrpcInstrumentorServer().instrument()
        GrpcInstrumentorClient().instrument()

        # Create tracer
        _tracer = trace.get_tracer(__name__)

        logger.info("tracing_initialized", endpoint=settings.otlp_endpoint)

    except Exception as e:
        logger.error("tracing_setup_failed", error=str(e))
        # Continue without tracing


def get_tracer() -> trace.Tracer | None:
    """
    Get the global tracer.

    Returns:
        Tracer instance or None if tracing not enabled
    """
    return _tracer


def shutdown_tracing() -> None:
    """Shutdown tracing and flush pending spans."""
    try:
        provider = trace.get_tracer_provider()
        if hasattr(provider, "shutdown"):
            provider.shutdown()
            logger.info("tracing_shutdown")
    except Exception as e:
        logger.error("tracing_shutdown_failed", error=str(e))
