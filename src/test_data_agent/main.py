"""Main entry point for Test Data Agent."""

import asyncio
import signal
import sys
from typing import Optional

from test_data_agent.config import get_settings
from test_data_agent.server.grpc_server import GrpcServer
from test_data_agent.server.health import HealthApp
from test_data_agent.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


class Application:
    """Main application that manages both gRPC and HTTP servers."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.grpc_server: Optional[GrpcServer] = None
        self.health_app: Optional[HealthApp] = None
        self.settings = get_settings()
        self.shutdown_event = asyncio.Event()

        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info("shutdown_signal_received", signal=signum)
        self.shutdown_event.set()

    async def start_grpc_server(self) -> None:
        """Start the gRPC server."""
        self.grpc_server = GrpcServer(self.settings)
        try:
            await self.grpc_server.start()
        except asyncio.CancelledError:
            logger.info("grpc_server_cancelled")
            if self.grpc_server:
                await self.grpc_server.stop()

    async def start_health_server(self) -> None:
        """Start the HTTP health server."""
        self.health_app = HealthApp(self.settings)
        try:
            await self.health_app.start()
        except asyncio.CancelledError:
            logger.info("health_server_cancelled")
            if self.health_app:
                await self.health_app.stop()

    async def run(self) -> None:
        """Run the application."""
        logger.info(
            "application_starting",
            service=self.settings.service_name,
            environment=self.settings.environment,
            grpc_port=self.settings.grpc_port,
            http_port=self.settings.http_port,
        )

        # Create tasks for both servers
        grpc_task = asyncio.create_task(self.start_grpc_server())
        health_task = asyncio.create_task(self.start_health_server())

        logger.info(
            "servers_started", grpc_port=self.settings.grpc_port, http_port=self.settings.http_port
        )

        # Wait for shutdown signal
        try:
            await self.shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("keyboard_interrupt_received")

        # Shutdown servers gracefully
        logger.info("application_shutting_down")

        # Cancel both tasks
        grpc_task.cancel()
        health_task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(grpc_task, health_task, return_exceptions=True)

        logger.info("application_stopped")


async def main() -> None:
    """Main application entry point."""
    # Load settings and setup logging
    settings = get_settings()
    setup_logging(log_level=settings.log_level, environment=settings.environment)

    logger.info(
        "test_data_agent_initializing",
        version="0.1.0",
        environment=settings.environment,
    )

    # Create and run application
    app = Application()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)
    except Exception as e:
        logger.error("application_error", error=str(e), exc_info=True)
        sys.exit(1)
