"""FastAPI health endpoints for Kubernetes probes and monitoring."""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
import uvicorn

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class HealthApp:
    """FastAPI application for health and metrics endpoints."""

    def __init__(self, settings: Settings):
        """
        Initialize health app.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.grpc_server_ready = False

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncIterator[None]:
            """Lifespan context manager."""
            logger.info("health_app_starting", port=settings.http_port)
            yield
            logger.info("health_app_stopping")

        self.app = FastAPI(
            title="Test Data Agent Health",
            description="Health and metrics endpoints",
            version="0.1.0",
            lifespan=lifespan,
        )

        # Add CORS middleware to allow browser requests
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],  # Allow Next.js dev server
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()
        logger.info("health_app_created", http_port=settings.http_port)

    def _setup_routes(self) -> None:
        """Set up HTTP routes."""

        @self.app.get("/health")
        async def health() -> dict[str, Any]:
            """
            General health endpoint.

            Returns:
                Health status and service info
            """
            return {
                "status": "healthy",
                "service": self.settings.service_name,
                "version": "0.1.0",
                "environment": self.settings.environment,
            }

        @self.app.get("/health/live")
        async def liveness() -> dict[str, str]:
            """
            Kubernetes liveness probe.
            Indicates if the service is running.

            Returns:
                Liveness status
            """
            return {"status": "ok"}

        @self.app.get("/health/ready")
        async def readiness(response: Response) -> dict[str, Any]:
            """
            Kubernetes readiness probe.
            Indicates if the service is ready to serve traffic.

            Returns:
                Readiness status
            """
            # Check if gRPC server is ready
            # In Phase 1, we'll assume ready if the app is running
            ready = True

            if not ready:
                response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
                return {
                    "status": "not_ready",
                    "reason": "gRPC server not ready",
                }

            return {
                "status": "ready",
                "grpc_port": self.settings.grpc_port,
            }

        @self.app.get("/metrics")
        async def metrics() -> Response:
            """
            Prometheus metrics endpoint.

            Returns:
                Prometheus metrics in text format
            """
            if not self.settings.prometheus_enabled:
                return PlainTextResponse("Metrics disabled", status_code=404)

            metrics_data = generate_latest()
            return Response(
                content=metrics_data,
                media_type=CONTENT_TYPE_LATEST,
            )

    def set_grpc_ready(self, ready: bool = True) -> None:
        """
        Set gRPC server readiness status.

        Args:
            ready: Whether gRPC server is ready
        """
        self.grpc_server_ready = ready
        logger.info("grpc_server_readiness_changed", ready=ready)

    async def start(self) -> None:
        """Start the FastAPI server."""
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.settings.http_port,
            log_level=self.settings.log_level.lower(),
            access_log=False,
        )
        server = uvicorn.Server(config)

        logger.info(
            "health_app_starting",
            host="0.0.0.0",
            port=self.settings.http_port,
        )

        await server.serve()

    async def stop(self) -> None:
        """Stop the FastAPI server."""
        logger.info("health_app_stopped")
