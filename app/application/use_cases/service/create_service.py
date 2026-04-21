from uuid import UUID

from app.application.dto.mappers import dto_to_service, service_to_dto
from app.application.dto.service_dto import ServiceCreateDTO, ServiceReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserNotFound


class CreateService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: ServiceCreateDTO, provider_id: UUID) -> ServiceReadDTO:
        async with self._uow:
            provider = await self._uow.users.get_by_id(provider_id)
            if not provider:
                raise UserNotFound(str(provider_id))
            service = dto_to_service(dto, provider_id=provider_id)
            saved = await self._uow.services.save(service)
            return service_to_dto(saved)
