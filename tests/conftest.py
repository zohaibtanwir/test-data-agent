"""Pytest configuration and shared fixtures."""

import os
import pytest
from typing import AsyncGenerator

from test_data_agent.config import load_settings, Settings


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = "test-api-key-for-testing"
    os.environ["ENVIRONMENT"] = "test"
    yield
    # Cleanup not needed as env vars are process-local


@pytest.fixture
def settings() -> Settings:
    """Fixture for test configuration."""
    return load_settings(
        anthropic_api_key="test-api-key",
        environment="test",
        log_level="INFO",
    )
