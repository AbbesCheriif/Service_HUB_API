from uuid import UUID

from app.application.dto.mappers import user_to_dto
from app.application.dto.user_dto import UserReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserNotFound


class GetUser:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> UserReadDTO:
        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFound(str(user_id))
            return user_to_dto(user)
