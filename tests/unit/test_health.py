"""Unit tests for health HTTP endpoints."""

import pytest
from fastapi.testclient import TestClient

from test_data_agent.config import load_settings
from test_data_agent.server.health import HealthApp


@pytest.fixture
def health_app():
    """Fixture for health app."""
    settings = load_settings(
        anthropic_api_key="test-key",
        prometheus_enabled=True,
    )
    return HealthApp(settings)


@pytest.fixture
def client(health_app):
    """Fixture for test client."""
    return TestClient(health_app.app)


def test_health_endpoint(client):
    """Test that /health endpoint returns service info."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "test-data-agent"
    assert "version" in data
    assert "environment" in data


def test_liveness_endpoint(client):
    """Test that /health/live returns OK."""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"


def test_readiness_endpoint(client):
    """Test that /health/ready returns ready status."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ready"
    assert "grpc_port" in data


def test_metrics_endpoint_enabled(client):
    """Test that /metrics endpoint returns Prometheus metrics when enabled."""
    response = client.get("/metrics")

    assert response.status_code == 200
    # Prometheus metrics are in text format
    assert response.headers["content-type"].startswith("text/plain")


def test_metrics_endpoint_disabled():
    """Test that /metrics endpoint returns 404 when disabled."""
    settings = load_settings(
        anthropic_api_key="test-key",
        prometheus_enabled=False,
    )
    app = HealthApp(settings)
    client = TestClient(app.app)

    response = client.get("/metrics")

    assert response.status_code == 404
    assert "disabled" in response.text.lower()
