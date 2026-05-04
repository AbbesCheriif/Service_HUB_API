import pytest
from uuid import uuid4

from app.application.use_cases.user.get_user import GetUser
from app.domain.exceptions import UserNotFound


@pytest.mark.asyncio
async def test_get_user_cache_miss_hits_db(mock_uow, mock_cache, sample_user):
    mock_cache.get.return_value = None
    mock_uow.users.get_by_id.return_value = sample_user

    use_case = GetUser(uow=mock_uow, cache=mock_cache)
    result = await use_case.execute(sample_user.id)

    assert result.id == sample_user.id
    assert result.email == str(sample_user.email)
    mock_uow.users.get_by_id.assert_called_once_with(sample_user.id)
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_cache_hit_skips_db(mock_uow, mock_cache, sample_user):
    cached_data = {
        "id": str(sample_user.id),
        "email": str(sample_user.email),
        "full_name": sample_user.full_name,
        "role": sample_user.role.value,
        "is_active": sample_user.is_active,
        "bio": sample_user.bio,
        "created_at": sample_user.created_at.isoformat(),
        "updated_at": sample_user.updated_at.isoformat(),
    }
    mock_cache.get.return_value = cached_data

    use_case = GetUser(uow=mock_uow, cache=mock_cache)
    result = await use_case.execute(sample_user.id)

    assert str(result.id) == str(sample_user.id)
    mock_uow.users.get_by_id.assert_not_called()
    mock_cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_not_found(mock_uow, mock_cache):
    mock_cache.get.return_value = None
    mock_uow.users.get_by_id.return_value = None

    use_case = GetUser(uow=mock_uow, cache=mock_cache)

    with pytest.raises(UserNotFound):
        await use_case.execute(uuid4())
