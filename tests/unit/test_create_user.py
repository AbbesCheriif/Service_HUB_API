import pytest

from app.application.dto.user_dto import UserCreateDTO
from app.application.use_cases.user.create_user import CreateUser
from app.domain.exceptions import UserAlreadyExists
from app.domain.value_objects.role import Role


@pytest.mark.asyncio
async def test_create_user_success(mock_uow, sample_user):
    mock_uow.users.get_by_email.return_value = None
    mock_uow.users.save.return_value = sample_user

    use_case = CreateUser(uow=mock_uow)
    dto = UserCreateDTO(
        email="alice@example.com",
        full_name="Alice Dupont",
        password="secret",
        role=Role.CLIENT,
    )

    result = await use_case.execute(dto, hashed_password="hashed_secret")

    assert result.email == "alice@example.com"
    assert result.full_name == "Alice Dupont"
    assert result.role == Role.CLIENT
    mock_uow.users.get_by_email.assert_called_once_with("alice@example.com")
    mock_uow.users.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_already_exists(mock_uow, sample_user):
    mock_uow.users.get_by_email.return_value = sample_user

    use_case = CreateUser(uow=mock_uow)
    dto = UserCreateDTO(
        email="alice@example.com",
        full_name="Alice Dupont",
        password="secret",
    )

    with pytest.raises(UserAlreadyExists):
        await use_case.execute(dto, hashed_password="hashed_secret")

    mock_uow.users.save.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_with_provider_role(mock_uow, sample_user):
    provider_user = sample_user
    provider_user.role = Role.PROVIDER
    mock_uow.users.get_by_email.return_value = None
    mock_uow.users.save.return_value = provider_user

    use_case = CreateUser(uow=mock_uow)
    dto = UserCreateDTO(
        email="provider@example.com",
        full_name="Bob Provider",
        password="secret",
        role=Role.PROVIDER,
    )

    result = await use_case.execute(dto, hashed_password="hashed_secret")

    assert result.role == Role.PROVIDER
