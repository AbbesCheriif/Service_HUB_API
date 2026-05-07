import functools
import json
from collections.abc import Callable
from typing import Any

from app.infrastructure.cache.redis_factory import RedisFactory


def cached(ttl: int = 300, key_prefix: str = ""):
    """Cache the return value of an async function in Redis.

    The cache key is built from key_prefix + the stringified positional and
    keyword arguments so that different call signatures map to distinct slots.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            raw_args = args[1:] if args and hasattr(args[0], "__class__") else args
            key_parts = [key_prefix or func.__qualname__]
            key_parts.extend(str(a) for a in raw_args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            client = RedisFactory.get_client()
            cached_value = await client.get(cache_key)
            if cached_value is not None:
                return json.loads(cached_value)

            result = await func(*args, **kwargs)
            await client.setex(cache_key, ttl, json.dumps(result, default=str))
            return result

        return wrapper

    return decorator
