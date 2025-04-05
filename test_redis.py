#!/usr/bin/env python3
"""Test script for Redis connectivity.

This script tests connection to Redis and basic cache operations.
"""

import asyncio
from src.services.redis_service import RedisService


async def test_redis():
    """Test Redis connectivity and basic operations."""
    print("Testing Redis connectivity...")

    # Test set and get
    await RedisService.set("test_key", "test_value")
    result = await RedisService.get("test_key")
    print(f"Set and get test: {'PASSED' if result == 'test_value' else 'FAILED'}")

    # Test delete
    await RedisService.delete("test_key")
    result = await RedisService.get("test_key")
    print(f"Delete test: {'PASSED' if result is None else 'FAILED'}")

    # Test serialization
    test_obj = {"name": "test", "value": 123}
    await RedisService.set("test_obj", test_obj)
    result = await RedisService.get("test_obj")
    print(f"Object serialization test: {'PASSED' if result == test_obj else 'FAILED'}")

    # Clean up
    await RedisService.delete("test_obj")
    await RedisService.close()

    print("Redis test completed.")


if __name__ == "__main__":
    asyncio.run(test_redis())
