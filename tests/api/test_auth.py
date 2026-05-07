from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import app.api.routers.auth as auth_router
from app.api.dependencies.database import get_session
from app.application.dto.user_dto import UserReadDTO
from app.application.use_cases.auth.login import TokenDTO
from app.domain.exceptions import InvalidCredentials, UserAlreadyExists
from app.main import app


@pytest.fixture(autouse=True)
def disable_rate_limit():
    async def noop():
        pass

    app.dependency_overrides[auth_router._auth_rate_limit] = noop
    yield
    app.dependency_overrides.pop(auth_router._auth_rate_limit, None)


@pytest.fixture
async def client():
    app.dependency_overrides[get_session] = lambda: MagicMock()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_register_success(client, sample_user):
    user_dto = UserReadDTO(
        id=sample_user.id,
        email=str(sample_user.email),
        full_name=sample_user.full_name,
        role=sample_user.role,
        is_active=sample_user.is_active,
        bio=None,
        created_at=sample_user.created_at,
        updated_at=sample_user.updated_at,
    )
    with patch("app.api.routers.auth.Register") as MockRegister:
        MockRegister.return_value.execute = AsyncMock(return_value=user_dto)
        response = await client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "full_name": "Alice Dupont",
                "password": "secret123",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Dupont"


async def test_register_duplicate_email(client):
    with patch("app.api.routers.auth.Register") as MockRegister:
        MockRegister.return_value.execute = AsyncMock(
            side_effect=UserAlreadyExists("alice@example.com")
        )
        response = await client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "full_name": "Alice Dupont",
                "password": "secret123",
            },
        )
    assert response.status_code == 409


async def test_register_invalid_email(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "full_name": "Alice",
            "password": "secret123",
        },
    )
    assert response.status_code == 422


async def test_login_success(client):
    token_dto = TokenDTO(
        access_token="access.token.here", refresh_token="refresh.token.here"
    )
    with patch("app.api.routers.auth.Login") as MockLogin:
        MockLogin.return_value.execute = AsyncMock(return_value=token_dto)
        response = await client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_credentials(client):
    with patch("app.api.routers.auth.Login") as MockLogin:
        MockLogin.return_value.execute = AsyncMock(side_effect=InvalidCredentials())
        response = await client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "wrong"},
        )
    assert response.status_code == 401


async def test_login_missing_fields(client):
    response = await client.post("/auth/login", json={"email": "alice@example.com"})
    assert response.status_code == 422
