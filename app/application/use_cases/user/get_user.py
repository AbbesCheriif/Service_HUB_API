from uuid import UUID

from app.application.dto.mappers import user_to_dto
from app.application.dto.user_dto import UserReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserNotFound
from app.infrastructure.cache.cache_service import CacheService


class GetUser:
    def __init__(self, uow: UnitOfWork, cache: CacheService) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(self, user_id: UUID) -> UserReadDTO:
        cache_key = f"user:{user_id}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return UserReadDTO.model_validate(cached)

        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFound(str(user_id))
            dto = user_to_dto(user)

        await self._cache.set(cache_key, dto.model_dump(mode="json"), ttl=300)
        return dto
