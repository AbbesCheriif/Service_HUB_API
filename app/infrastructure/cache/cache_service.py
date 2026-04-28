import json
from typing import Any

from app.infrastructure.cache.redis_factory import RedisFactory


class CacheService:
    def __init__(self) -> None:
        self._client = RedisFactory.get_client()

    async def get(self, key: str) -> Any | None:
        value = await self._client.get(key)
        return json.loads(value) if value is not None else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self._client.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def invalidate_pattern(self, pattern: str) -> int:
        keys = await self._client.keys(pattern)
        if not keys:
            return 0
        return await self._client.delete(*keys)
