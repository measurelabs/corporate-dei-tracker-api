"""Redis client configuration and utilities."""
import json
from typing import Optional, Any
from upstash_redis import Redis
from app.config import get_settings

settings = get_settings()

# Initialize Upstash Redis client
redis_client = Redis(
    url=settings.upstash_redis_rest_url,
    token=settings.upstash_redis_rest_token
)


def get_redis() -> Redis:
    """Get Redis client instance."""
    return redis_client


async def get_cache(key: str) -> Optional[Any]:
    """
    Get value from Redis cache.

    Args:
        key: Cache key

    Returns:
        Cached value if exists, None otherwise
    """
    try:
        value = redis_client.get(key)
        if value:
            # Upstash Redis returns strings, parse JSON if needed
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
    except Exception as e:
        print(f"Redis GET error: {e}")
        return None


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set value in Redis cache with optional TTL.

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (default from settings)

    Returns:
        True if successful, False otherwise
    """
    try:
        ttl = ttl or settings.redis_cache_ttl

        # Serialize value to JSON
        if not isinstance(value, str):
            value = json.dumps(value)

        redis_client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        print(f"Redis SET error: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """
    Delete value from Redis cache.

    Args:
        key: Cache key

    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis DELETE error: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> bool:
    """
    Delete all keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "analytics:*")

    Returns:
        True if successful, False otherwise
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Redis CLEAR PATTERN error: {e}")
        return False
