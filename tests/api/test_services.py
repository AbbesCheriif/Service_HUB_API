from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_session
from app.application.dto.service_dto import ServiceReadDTO
from app.domain.value_objects.role import Role
from app.main import app


def _make_service_dto(**kwargs) -> ServiceReadDTO:
    now = datetime.now(timezone.utc)
    return ServiceReadDTO(
        id=kwargs.get("id", uuid4()),
        provider_id=kwargs.get("provider_id", uuid4()),
        title=kwargs.get("title", "Test Service"),
        description=kwargs.get("description", "A test service"),
        price=kwargs.get("price", 50.0),
        duration_minutes=kwargs.get("duration_minutes", 60),
        is_active=kwargs.get("is_active", True),
        category=kwargs.get("category", "Test"),
        average_rating=0.0,
        total_reviews=0,
        created_at=kwargs.get("created_at", now),
        updated_at=kwargs.get("updated_at", now),
    )


@pytest.fixture
async def client():
    app.dependency_overrides[get_session] = lambda: MagicMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def provider_client(sample_user):
    sample_user_copy = sample_user
    sample_user_copy.role = Role.PROVIDER
    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_current_user] = lambda: sample_user_copy
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_list_services_empty(client):
    with patch("app.api.routers.services.ListServices") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=[])
        response = await client.get("/services/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 1


async def test_list_services_with_results(client):
    service_dto = _make_service_dto(title="Massage")
    with patch("app.api.routers.services.ListServices") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=[service_dto])
        response = await client.get("/services/")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Massage"


async def test_get_service_not_found(client):
    service_id = uuid4()
    mock_uow_inst = MagicMock()
    mock_uow_inst.__aenter__ = AsyncMock(return_value=mock_uow_inst)
    mock_uow_inst.__aexit__ = AsyncMock(return_value=False)
    mock_uow_inst.services.get_by_id = AsyncMock(return_value=None)
    with patch("app.api.routers.services.SQLAlchemyUnitOfWork", return_value=mock_uow_inst):
        response = await client.get(f"/services/{service_id}")
    assert response.status_code == 404


async def test_get_service_success(client):
    service_dto = _make_service_dto()
    mock_uow_inst = MagicMock()
    mock_uow_inst.__aenter__ = AsyncMock(return_value=mock_uow_inst)
    mock_uow_inst.__aexit__ = AsyncMock(return_value=False)
    mock_uow_inst.services.get_by_id = AsyncMock(return_value=service_dto)
    with patch("app.api.routers.services.SQLAlchemyUnitOfWork", return_value=mock_uow_inst):
        response = await client.get(f"/services/{service_dto.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Service"


async def test_create_service_requires_auth(client):
    response = await client.post(
        "/services/",
        json={"title": "New Service", "description": "Desc", "price": 100.0},
    )
    assert response.status_code == 401


async def test_create_service_success(provider_client):
    service_dto = _make_service_dto(title="New Service", price=100.0)
    with patch("app.api.routers.services.CreateService") as MockUseCase:
        MockUseCase.return_value.execute = AsyncMock(return_value=service_dto)
        response = await provider_client.post(
            "/services/",
            json={"title": "New Service", "description": "Desc", "price": 100.0},
        )
    assert response.status_code == 201
    assert response.json()["title"] == "New Service"
    assert response.json()["price"] == 100.0


async def test_create_service_invalid_price(provider_client):
    response = await provider_client.post(
        "/services/",
        json={"title": "Bad Service", "description": "Desc", "price": -10.0},
    )
    assert response.status_code == 422
