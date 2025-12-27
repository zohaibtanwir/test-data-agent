"""Redis client for caching and data pools."""

import json
from typing import Any

import redis.asyncio as redis

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Async Redis client for caching and data pooling."""

    def __init__(self, settings: Settings):
        """Initialize Redis client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.client: redis.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis server."""
        try:
            self.client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self.client.ping()
            logger.info("redis_connected", url=self.settings.redis_url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            # Don't raise - continue without cache
            self.client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.client:
            await self.client.close()
            logger.info("redis_disconnected")

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                logger.debug("cache_hit", key=key)
            else:
                logger.debug("cache_miss", key=key)
            return value
        except Exception as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
        """
        if not self.client:
            return

        try:
            ttl = ttl or self.settings.cache_ttl_seconds
            await self.client.set(key, value, ex=ttl)
            logger.debug("cache_set", key=key, ttl=ttl)
        except Exception as e:
            logger.error("cache_set_failed", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        """Delete key from cache.

        Args:
            key: Cache key
        """
        if not self.client:
            return

        try:
            await self.client.delete(key)
            logger.debug("cache_deleted", key=key)
        except Exception as e:
            logger.error("cache_delete_failed", key=key, error=str(e))

    async def get_from_pool(self, pool_name: str, count: int) -> list[dict]:
        """Get items from data pool.

        Args:
            pool_name: Name of the pool (e.g., 'addresses', 'phones')
            count: Number of items to retrieve

        Returns:
            List of data items (may be fewer than requested if pool is small)
        """
        if not self.client:
            return []

        try:
            pool_key = f"pool:{pool_name}"
            items = await self.client.lrange(pool_key, 0, count - 1)

            # Remove retrieved items from pool
            if items:
                await self.client.ltrim(pool_key, len(items), -1)

            parsed_items = [json.loads(item) for item in items]
            logger.debug("pool_get", pool=pool_name, requested=count, retrieved=len(parsed_items))
            return parsed_items

        except Exception as e:
            logger.error("pool_get_failed", pool=pool_name, error=str(e))
            return []

    async def add_to_pool(self, pool_name: str, data: list[dict]) -> None:
        """Add items to data pool.

        Args:
            pool_name: Name of the pool
            data: List of data items to add
        """
        if not self.client:
            return

        try:
            pool_key = f"pool:{pool_name}"
            serialized = [json.dumps(item) for item in data]

            # Add to pool
            if serialized:
                await self.client.rpush(pool_key, *serialized)

                # Set TTL if not already set
                ttl = await self.client.ttl(pool_key)
                if ttl == -1:  # No TTL set
                    await self.client.expire(pool_key, self.settings.cache_ttl_seconds)

            logger.debug("pool_add", pool=pool_name, count=len(data))

        except Exception as e:
            logger.error("pool_add_failed", pool=pool_name, error=str(e))

    async def get_pool_size(self, pool_name: str) -> int:
        """Get current size of a pool.

        Args:
            pool_name: Name of the pool

        Returns:
            Number of items in pool
        """
        if not self.client:
            return 0

        try:
            pool_key = f"pool:{pool_name}"
            size = await self.client.llen(pool_key)
            return size
        except Exception as e:
            logger.error("pool_size_failed", pool=pool_name, error=str(e))
            return 0

    def build_cache_key(self, domain: str, entity: str, **kwargs: Any) -> str:
        """Build cache key from request parameters.

        Args:
            domain: Domain name
            entity: Entity name
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        parts = [domain, entity]
        for key in sorted(kwargs.keys()):
            parts.append(f"{key}:{kwargs[key]}")
        return ":".join(parts)
