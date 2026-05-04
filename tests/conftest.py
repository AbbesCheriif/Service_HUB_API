import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.entities.booking import Booking
from app.domain.entities.service import Service
from app.domain.entities.user import User
from app.domain.value_objects.booking_status import BookingStatus
from app.domain.value_objects.email import Email
from app.domain.value_objects.role import Role


class MockUserRepository:
    def __init__(self):
        self.get_by_email = AsyncMock(return_value=None)
        self.get_by_id = AsyncMock(return_value=None)
        self.save = AsyncMock()


class MockServiceRepository:
    def __init__(self):
        self.get_by_id = AsyncMock(return_value=None)


class MockBookingRepository:
    def __init__(self):
        self.get_by_id = AsyncMock(return_value=None)
        self.has_conflict = AsyncMock(return_value=False)
        self.save = AsyncMock()


class MockUnitOfWork:
    def __init__(self):
        self.users = MockUserRepository()
        self.services = MockServiceRepository()
        self.bookings = MockBookingRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


class MockCacheService:
    def __init__(self):
        self.get = AsyncMock(return_value=None)
        self.set = AsyncMock()
        self.delete = AsyncMock()
        self.invalidate_pattern = AsyncMock()


@pytest.fixture
def mock_uow():
    return MockUnitOfWork()


@pytest.fixture
def mock_cache():
    return MockCacheService()


@pytest.fixture
def sample_user():
    return User(
        id=uuid4(),
        email=Email("alice@example.com"),
        full_name="Alice Dupont",
        hashed_password="hashed_pw",
        role=Role.CLIENT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_service():
    return Service(
        id=uuid4(),
        provider_id=uuid4(),
        title="Massage thérapeutique",
        description="Séance de 60 minutes",
        price=50.0,
        duration_minutes=60,
        is_active=True,
        category="Bien-être",
    )


@pytest.fixture
def sample_booking(sample_service):
    return Booking(
        id=uuid4(),
        client_id=uuid4(),
        service_id=sample_service.id,
        provider_id=sample_service.provider_id,
        scheduled_at=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        status=BookingStatus.PENDING,
        total_price=sample_service.price,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
