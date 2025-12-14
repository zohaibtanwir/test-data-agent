"""Configuration management using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Settings
    service_name: str = "test-data-agent"
    grpc_port: int = 9091
    http_port: int = 8091
    log_level: str = "INFO"
    environment: str = "development"

    # LLM - Claude
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # LLM - Local vLLM
    vllm_base_url: str = "http://vllm:8000/v1"
    vllm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    use_local_llm: bool = False

    # RAG - Weaviate
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: str | None = None
    rag_collection_patterns: str = "testdata_patterns"
    rag_collection_defects: str = "testdata_defects"
    rag_top_k: int = 5

    # Cache - Redis
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 86400  # 24 hours

    # Generation
    max_sync_records: int = 1000
    default_batch_size: int = 50
    coherence_threshold: float = 0.85

    # Observability
    prometheus_enabled: bool = True
    tracing_enabled: bool = True
    otlp_endpoint: str = "http://otel-collector:4317"


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore
    return _settings


def load_settings(**kwargs) -> Settings:
    """Load settings with optional overrides for testing."""
    return Settings(**kwargs)  # type: ignore
