"""Redis service for caching.

This module provides Redis caching functionality for the application.
"""

import json
import pickle
from typing import Any, Optional, TypeVar, Generic
import redis.asyncio as redis

from src.conf.config import settings

T = TypeVar("T")


class RedisService:
    """Service for interacting with Redis cache.

    This class provides methods for getting, setting, and deleting cache entries.
    Uses a singleton pattern to ensure only one Redis connection is created.
    """

    # Class-level redis client (singleton)
    _redis_client = None

    @classmethod
    def _get_client(cls):
        """Get or initialize the Redis client.

        Returns:
            redis.Redis: Redis client instance
        """
        if cls._redis_client is None:
            cls._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,  # We need this for binary data (pickle)
            )
        return cls._redis_client

    @classmethod
    async def get(cls, key: str) -> dict | str | int | None:
        """Get a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            dict | str | int | None: Cached value if exists, None otherwise
        """
        data = await cls._get_client().get(key)
        if data is None:
            return None
        try:
            return pickle.loads(data)
        except Exception:
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (Optional[int]): Time to live in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized_data = pickle.dumps(value)
            if ttl is None:
                ttl = settings.REDIS_USER_CACHE_TTL
            await cls._get_client().set(key, serialized_data, ex=ttl)
            return True
        except Exception:
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await cls._get_client().delete(key)
            return True
        except Exception:
            return False

    @classmethod
    async def close(cls):
        """Close the Redis connection."""
        if cls._redis_client is not None:
            await cls._redis_client.close()
            cls._redis_client = None
