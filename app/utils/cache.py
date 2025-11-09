"""Caching utilities and decorators."""
from functools import wraps
from typing import Optional, Callable
from app.redis_client import get_cache, set_cache


def cached(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results in Redis.

    Args:
        key_prefix: Prefix for the cache key
        ttl: Time to live in seconds (None = use default from settings)
        key_builder: Optional function to build cache key from args/kwargs

    Usage:
        @cached("analytics:overview", ttl=600)
        async def get_overview_stats():
            ...

        @cached("company", key_builder=lambda company_id: f"company:{company_id}")
        async def get_company(company_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use prefix and stringified args
                args_str = "_".join(str(arg) for arg in args if arg is not None)
                kwargs_str = "_".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
                suffix = "_".join(filter(None, [args_str, kwargs_str]))
                cache_key = f"{key_prefix}:{suffix}" if suffix else key_prefix

            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await set_cache(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def build_query_cache_key(prefix: str, **params) -> str:
    """
    Build a cache key from query parameters.

    Args:
        prefix: Key prefix
        **params: Query parameters to include in key

    Returns:
        Formatted cache key
    """
    # Filter out None values and build key
    filtered_params = {k: v for k, v in params.items() if v is not None}
    if not filtered_params:
        return prefix

    params_str = "_".join(f"{k}={v}" for k, v in sorted(filtered_params.items()))
    return f"{prefix}:{params_str}"
