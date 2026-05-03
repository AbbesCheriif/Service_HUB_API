import time

from fastapi import HTTPException, status
from starlette.requests import Request

from app.infrastructure.cache.redis_factory import RedisFactory


class RateLimiter:
    """Sliding window rate limiter usable as a FastAPI dependency.

    Tracks requests per (route, client IP) using a Redis sorted set.
    Each member is the request timestamp; expired entries are pruned on
    every call so the window always reflects the last `window_seconds`.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{request.url.path}:{client_ip}"
        now = time.time()
        window_start = now - self.window_seconds

        redis = RedisFactory.get_client()
        try:
            await redis.zremrangebyscore(key, 0, window_start)
            count = await redis.zcard(key)
            if count >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(self.window_seconds)},
                )
            await redis.zadd(key, {str(now): now})
            await redis.expire(key, self.window_seconds)
        finally:
            await redis.aclose()
