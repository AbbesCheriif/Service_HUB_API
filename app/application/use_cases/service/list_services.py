from app.application.dto.mappers import service_to_dto
from app.application.dto.service_dto import ServiceReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork


class ListServices:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, offset: int = 0, limit: int = 20) -> list[ServiceReadDTO]:
        async with self._uow:
            services = await self._uow.services.list_active(offset=offset, limit=limit)
            return [service_to_dto(s) for s in services]
