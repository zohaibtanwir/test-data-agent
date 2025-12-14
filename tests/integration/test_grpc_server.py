"""Integration tests for gRPC server."""

import asyncio

import grpc
import pytest

from test_data_agent.config import load_settings
from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc
from test_data_agent.server.grpc_server import GrpcServer


@pytest.fixture
async def grpc_server():
    """Fixture to start and stop gRPC server for testing."""
    settings = load_settings(
        anthropic_api_key="test-key-for-grpc-test",
        grpc_port=50051,  # Use different port for testing
        http_port=8082,
    )

    server = GrpcServer(settings)

    # Start server in background
    server_task = asyncio.create_task(server.start())

    # Give server time to start
    await asyncio.sleep(0.5)

    yield settings

    # Stop server
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_health_check_rpc(grpc_server):
    """Test that HealthCheck RPC returns healthy status."""
    settings = grpc_server

    async with grpc.aio.insecure_channel(f"localhost:{settings.grpc_port}") as channel:
        stub = test_data_pb2_grpc.TestDataServiceStub(channel)

        request = test_data_pb2.HealthCheckRequest()
        response = await stub.HealthCheck(request)

        assert response.status == "healthy"
        assert "grpc_server" in response.components
        assert response.components["grpc_server"] == "healthy"


@pytest.mark.asyncio
async def test_generate_data_functional(grpc_server):
    """Test that GenerateData RPC generates actual data."""
    settings = grpc_server

    async with grpc.aio.insecure_channel(f"localhost:{settings.grpc_port}") as channel:
        stub = test_data_pb2_grpc.TestDataServiceStub(channel)

        request = test_data_pb2.GenerateRequest(
            request_id="test-001",
            domain="ecommerce",
            entity="cart",
            count=10,
        )
        response = await stub.GenerateData(request)

        assert response.success is True
        assert response.request_id == "test-001"
        assert response.record_count == 10
        assert response.metadata.generation_path == "traditional"

        # Parse and verify data
        import json

        data = json.loads(response.data)
        assert len(data) == 10
        assert "cart_id" in data[0]


@pytest.mark.asyncio
async def test_get_schemas_returns_schemas(grpc_server):
    """Test that GetSchemas RPC returns available schemas."""
    settings = grpc_server

    async with grpc.aio.insecure_channel(f"localhost:{settings.grpc_port}") as channel:
        stub = test_data_pb2_grpc.TestDataServiceStub(channel)

        request = test_data_pb2.GetSchemasRequest()
        response = await stub.GetSchemas(request)

        # Should return 5 schemas (cart, order, payment, user, review)
        assert len(response.schemas) == 5

        # Verify schema structure
        schema_names = {s.name for s in response.schemas}
        assert "cart" in schema_names
        assert "order" in schema_names
        assert "payment" in schema_names
