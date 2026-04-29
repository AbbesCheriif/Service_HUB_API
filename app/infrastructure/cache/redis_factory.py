from redis.asyncio import ConnectionPool, Redis

from app.core.config.settings import get_settings


class RedisFactory:
    _pool: ConnectionPool | None = None

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        if cls._pool is None:
            settings = get_settings()
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=20,
            )
        return cls._pool

    @classmethod
    def get_client(cls) -> Redis:
        return Redis(connection_pool=cls.get_pool())

    @classmethod
    async def close(cls) -> None:
        if cls._pool is not None:
            await cls._pool.disconnect()
            cls._pool = None
