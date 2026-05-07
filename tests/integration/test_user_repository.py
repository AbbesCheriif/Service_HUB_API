import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.infrastructure.database.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.role import Role
from app.infrastructure.database.models.base import Base
from app.infrastructure.repositories.user_repository_impl import (
    SQLAlchemyUserRepository,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/servicehub_test",
)

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture(scope="module")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(test_engine):
    factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def repo(session):
    return SQLAlchemyUserRepository(session)


def _make_user(**kwargs) -> User:
    now = datetime.now(UTC)
    defaults = dict(
        id=uuid4(),
        email=Email(f"user_{uuid4().hex[:8]}@example.com"),
        full_name="Test User",
        hashed_password="$2b$12$fakehashed",
        role=Role.CLIENT,
        is_active=True,
        bio=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return User(**defaults)


async def test_save_and_get_by_id(repo, session):
    user = _make_user()
    saved = await repo.save(user)
    await session.flush()

    fetched = await repo.get_by_id(saved.id)

    assert fetched is not None
    assert fetched.id == saved.id
    assert str(fetched.email) == str(saved.email)
    assert fetched.full_name == saved.full_name


async def test_get_by_email(repo, session):
    user = _make_user()
    await repo.save(user)
    await session.flush()

    fetched = await repo.get_by_email(str(user.email))

    assert fetched is not None
    assert str(fetched.email) == str(user.email)


async def test_get_by_id_returns_none_for_unknown(repo):
    result = await repo.get_by_id(uuid4())
    assert result is None


async def test_get_by_email_returns_none_for_unknown(repo):
    result = await repo.get_by_email("nobody@example.com")
    assert result is None


async def test_update_user(repo, session):
    user = _make_user()
    saved = await repo.save(user)
    await session.flush()

    saved.full_name = "Updated Name"
    await repo.save(saved)
    await session.flush()

    fetched = await repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.full_name == "Updated Name"


async def test_delete_user(repo, session):
    user = _make_user()
    saved = await repo.save(user)
    await session.flush()

    await repo.delete(saved.id)
    await session.flush()

    result = await repo.get_by_id(saved.id)
    assert result is None


async def test_list_all_returns_saved_users(repo, session):
    for _ in range(3):
        await repo.save(_make_user())
    await session.flush()

    users = await repo.list_all(offset=0, limit=100)
    assert len(users) >= 3


async def test_list_all_pagination(repo, session):
    for _ in range(5):
        await repo.save(_make_user())
    await session.flush()

    page1 = await repo.list_all(offset=0, limit=2)
    page2 = await repo.list_all(offset=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert {u.id for u in page1}.isdisjoint({u.id for u in page2})
