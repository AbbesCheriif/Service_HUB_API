from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.database.engine import engine


class AsyncSessionFactory:
    _factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_factory(cls) -> async_sessionmaker[AsyncSession]:
        if cls._factory is None:
            cls._factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return cls._factory

    @classmethod
    def create_session(cls) -> AsyncSession:
        return cls.get_factory()()
