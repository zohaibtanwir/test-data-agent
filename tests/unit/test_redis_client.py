"""Unit tests for Redis client."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from test_data_agent.clients.redis_client import RedisClient
from test_data_agent.config import load_settings


@pytest.fixture
def settings():
    """Create test settings."""
    return load_settings(
        anthropic_api_key="test-key",
        redis_url="redis://localhost:6379/0",
        cache_ttl_seconds=3600,
    )


@pytest.fixture
def redis_client(settings):
    """Create Redis client."""
    return RedisClient(settings)


@pytest.mark.asyncio
async def test_connect_success(redis_client):
    """Test successful Redis connection."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_from_url.return_value = mock_redis

        await redis_client.connect()

        assert redis_client.client is not None
        mock_from_url.assert_called_once()
        mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_connect_failure(redis_client):
    """Test Redis connection failure."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_from_url.side_effect = Exception("Connection failed")

        await redis_client.connect()

        # Should not raise, client should be None
        assert redis_client.client is None


@pytest.mark.asyncio
async def test_disconnect(redis_client):
    """Test Redis disconnection."""
    mock_redis = AsyncMock()
    redis_client.client = mock_redis

    await redis_client.disconnect()

    mock_redis.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_cache_hit(redis_client):
    """Test cache get with hit."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="cached_value")
    redis_client.client = mock_redis

    result = await redis_client.get("test_key")

    assert result == "cached_value"
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_cache_miss(redis_client):
    """Test cache get with miss."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    redis_client.client = mock_redis

    result = await redis_client.get("test_key")

    assert result is None


@pytest.mark.asyncio
async def test_get_no_client(redis_client):
    """Test get when client not connected."""
    redis_client.client = None

    result = await redis_client.get("test_key")

    assert result is None


@pytest.mark.asyncio
async def test_set_cache(redis_client):
    """Test cache set."""
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock()
    redis_client.client = mock_redis

    await redis_client.set("test_key", "test_value", ttl=60)

    mock_redis.set.assert_called_once_with("test_key", "test_value", ex=60)


@pytest.mark.asyncio
async def test_set_default_ttl(redis_client):
    """Test cache set with default TTL."""
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock()
    redis_client.client = mock_redis

    await redis_client.set("test_key", "test_value")

    mock_redis.set.assert_called_once_with("test_key", "test_value", ex=3600)


@pytest.mark.asyncio
async def test_delete_cache(redis_client):
    """Test cache delete."""
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock()
    redis_client.client = mock_redis

    await redis_client.delete("test_key")

    mock_redis.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_from_pool(redis_client):
    """Test getting items from pool."""
    mock_redis = AsyncMock()
    test_data = [{"name": "John"}, {"name": "Jane"}]
    serialized = [json.dumps(item) for item in test_data]

    mock_redis.lrange = AsyncMock(return_value=serialized)
    mock_redis.ltrim = AsyncMock()
    redis_client.client = mock_redis

    result = await redis_client.get_from_pool("names", 2)

    assert len(result) == 2
    assert result[0]["name"] == "John"
    assert result[1]["name"] == "Jane"
    mock_redis.lrange.assert_called_once_with("pool:names", 0, 1)
    mock_redis.ltrim.assert_called_once_with("pool:names", 2, -1)


@pytest.mark.asyncio
async def test_get_from_pool_empty(redis_client):
    """Test getting from empty pool."""
    mock_redis = AsyncMock()
    mock_redis.lrange = AsyncMock(return_value=[])
    redis_client.client = mock_redis

    result = await redis_client.get_from_pool("names", 5)

    assert result == []


@pytest.mark.asyncio
async def test_add_to_pool(redis_client):
    """Test adding items to pool."""
    mock_redis = AsyncMock()
    mock_redis.rpush = AsyncMock()
    mock_redis.ttl = AsyncMock(return_value=-1)
    mock_redis.expire = AsyncMock()
    redis_client.client = mock_redis

    test_data = [{"name": "Alice"}, {"name": "Bob"}]
    await redis_client.add_to_pool("names", test_data)

    # Verify rpush was called with serialized data
    mock_redis.rpush.assert_called_once()
    call_args = mock_redis.rpush.call_args[0]
    assert call_args[0] == "pool:names"

    # Verify TTL was set
    mock_redis.expire.assert_called_once_with("pool:names", 3600)


@pytest.mark.asyncio
async def test_get_pool_size(redis_client):
    """Test getting pool size."""
    mock_redis = AsyncMock()
    mock_redis.llen = AsyncMock(return_value=42)
    redis_client.client = mock_redis

    size = await redis_client.get_pool_size("names")

    assert size == 42
    mock_redis.llen.assert_called_once_with("pool:names")


def test_build_cache_key(redis_client):
    """Test cache key building."""
    key = redis_client.build_cache_key("ecommerce", "cart", scenario="default", count=10)

    assert "ecommerce" in key
    assert "cart" in key
    assert "count:10" in key
    assert "scenario:default" in key
