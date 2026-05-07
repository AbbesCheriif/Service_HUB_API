from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_session
from app.application.dto.booking_dto import BookingReadDTO
from app.domain.value_objects.booking_status import BookingStatus
from app.domain.value_objects.role import Role
from app.main import app


def _make_booking_dto(client_id=None, provider_id=None, **kwargs) -> BookingReadDTO:
    now = datetime.now(UTC)
    return BookingReadDTO(
        id=kwargs.get("id", uuid4()),
        client_id=client_id or uuid4(),
        service_id=kwargs.get("service_id", uuid4()),
        provider_id=provider_id or uuid4(),
        scheduled_at=kwargs.get(
            "scheduled_at", datetime(2026, 8, 1, 10, 0, tzinfo=UTC)
        ),
        status=kwargs.get("status", BookingStatus.PENDING),
        notes=kwargs.get("notes", None),
        total_price=kwargs.get("total_price", 50.0),
        created_at=kwargs.get("created_at", now),
        updated_at=kwargs.get("updated_at", now),
    )


@pytest.fixture
async def client_user_client(sample_user):
    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_current_user] = lambda: sample_user
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def provider_user_client(sample_user):
    sample_user.role = Role.PROVIDER
    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_current_user] = lambda: sample_user
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def anon_client():
    app.dependency_overrides[get_session] = lambda: MagicMock()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def test_list_bookings_requires_auth(anon_client):
    response = await anon_client.get("/bookings/")
    assert response.status_code == 401


async def test_create_booking_requires_auth(anon_client):
    response = await anon_client.post(
        "/bookings/",
        json={
            "service_id": str(uuid4()),
            "scheduled_at": "2026-08-01T10:00:00Z",
        },
    )
    assert response.status_code == 401


async def test_create_booking_success(client_user_client, sample_user):
    booking_dto = _make_booking_dto(client_id=sample_user.id)
    with patch("app.api.routers.bookings.CreateBooking") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=booking_dto)
        response = await client_user_client.post(
            "/bookings/",
            json={
                "service_id": str(uuid4()),
                "scheduled_at": "2026-08-01T10:00:00Z",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == BookingStatus.PENDING.value
    assert data["total_price"] == 50.0


async def test_list_bookings_as_client(client_user_client, sample_user):
    booking_dto = _make_booking_dto(client_id=sample_user.id)
    mock_uow_inst = MagicMock()
    mock_uow_inst.__aenter__ = AsyncMock(return_value=mock_uow_inst)
    mock_uow_inst.__aexit__ = AsyncMock(return_value=False)
    mock_uow_inst.bookings.get_by_client = AsyncMock(return_value=[booking_dto])
    with patch(
        "app.api.routers.bookings.SQLAlchemyUnitOfWork", return_value=mock_uow_inst
    ):
        response = await client_user_client.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_accept_booking_success(provider_user_client, sample_user):
    booking_id = uuid4()
    booking_dto = _make_booking_dto(
        id=booking_id,
        provider_id=sample_user.id,
        status=BookingStatus.CONFIRMED,
    )
    with patch("app.api.routers.bookings.AcceptBooking") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=booking_dto)
        response = await provider_user_client.post(f"/bookings/{booking_id}/accept")
    assert response.status_code == 200
    assert response.json()["status"] == BookingStatus.CONFIRMED.value


async def test_cancel_booking_success(client_user_client, sample_user):
    booking_id = uuid4()
    booking_dto = _make_booking_dto(
        id=booking_id,
        client_id=sample_user.id,
        status=BookingStatus.CANCELLED,
    )
    with patch("app.api.routers.bookings.CancelBooking") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=booking_dto)
        response = await client_user_client.post(f"/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == BookingStatus.CANCELLED.value


async def test_accept_booking_requires_provider_role(client_user_client):
    booking_id = uuid4()
    response = await client_user_client.post(f"/bookings/{booking_id}/accept")
    assert response.status_code == 403
