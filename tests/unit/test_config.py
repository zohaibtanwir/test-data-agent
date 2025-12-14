"""Unit tests for configuration management."""

import os
import pytest
from pydantic import ValidationError

from test_data_agent.config import Settings, load_settings


def test_config_loads_defaults():
    """Test that configuration loads with default values."""
    settings = load_settings(anthropic_api_key="test-key-12345")

    assert settings.service_name == "test-data-agent"
    assert settings.grpc_port == 9091
    assert settings.http_port == 8091
    assert settings.log_level == "INFO"
    # Environment can be test or development depending on conftest
    assert settings.environment in ["development", "test"]
    assert settings.anthropic_api_key == "test-key-12345"
    assert settings.claude_model == "claude-sonnet-4-20250514"
    assert settings.max_sync_records == 1000
    assert settings.coherence_threshold == 0.85


def test_config_loads_from_env():
    """Test that configuration loads from environment variables."""
    # Set environment variables
    os.environ["ANTHROPIC_API_KEY"] = "custom-api-key"
    os.environ["SERVICE_NAME"] = "custom-service"
    os.environ["GRPC_PORT"] = "9999"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["CLAUDE_MAX_TOKENS"] = "8192"

    settings = load_settings()

    assert settings.anthropic_api_key == "custom-api-key"
    assert settings.service_name == "custom-service"
    assert settings.grpc_port == 9999
    assert settings.log_level == "DEBUG"
    assert settings.environment == "production"
    assert settings.claude_max_tokens == 8192

    # Cleanup
    for key in [
        "ANTHROPIC_API_KEY",
        "SERVICE_NAME",
        "GRPC_PORT",
        "LOG_LEVEL",
        "ENVIRONMENT",
        "CLAUDE_MAX_TOKENS",
    ]:
        if key in os.environ:
            del os.environ[key]


def test_config_requires_api_key(monkeypatch, tmp_path):
    """Test that configuration raises error when API key is missing."""
    # Remove API key from environment
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Change to temp directory to avoid loading .env file
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    assert "anthropic_api_key" in str(exc_info.value).lower()


def test_config_with_overrides():
    """Test that configuration can be loaded with programmatic overrides."""
    settings = load_settings(
        anthropic_api_key="override-key",
        grpc_port=7777,
        log_level="WARNING",
    )

    assert settings.anthropic_api_key == "override-key"
    assert settings.grpc_port == 7777
    assert settings.log_level == "WARNING"


def test_config_type_conversion():
    """Test that configuration correctly converts types from environment."""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["GRPC_PORT"] = "8888"
    os.environ["USE_LOCAL_LLM"] = "true"
    os.environ["COHERENCE_THRESHOLD"] = "0.95"

    settings = load_settings()

    assert isinstance(settings.grpc_port, int)
    assert settings.grpc_port == 8888
    assert isinstance(settings.use_local_llm, bool)
    assert settings.use_local_llm is True
    assert isinstance(settings.coherence_threshold, float)
    assert settings.coherence_threshold == 0.95

    # Cleanup
    for key in ["ANTHROPIC_API_KEY", "GRPC_PORT", "USE_LOCAL_LLM", "COHERENCE_THRESHOLD"]:
        if key in os.environ:
            del os.environ[key]
