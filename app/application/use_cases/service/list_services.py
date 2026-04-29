from app.application.dto.mappers import service_to_dto
from app.application.dto.service_dto import ServiceReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.cache.cache_service import CacheService


class ListServices:
    def __init__(self, uow: UnitOfWork, cache: CacheService) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(self, offset: int = 0, limit: int = 20) -> list[ServiceReadDTO]:
        cache_key = f"services:list:{offset}:{limit}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return [ServiceReadDTO.model_validate(item) for item in cached]

        async with self._uow:
            services = await self._uow.services.list_active(offset=offset, limit=limit)
            dtos = [service_to_dto(s) for s in services]

        await self._cache.set(cache_key, [dto.model_dump(mode="json") for dto in dtos], ttl=300)
        return dtos
