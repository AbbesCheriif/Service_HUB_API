from app.application.dto.mappers import dto_to_user, user_to_dto
from app.application.dto.user_dto import UserCreateDTO, UserReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserAlreadyExists


class CreateUser:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: UserCreateDTO, hashed_password: str) -> UserReadDTO:
        async with self._uow:
            existing = await self._uow.users.get_by_email(dto.email)
            if existing:
                raise UserAlreadyExists(dto.email)
            user = dto_to_user(dto, hashed_password=hashed_password)
            saved = await self._uow.users.save(user)
            return user_to_dto(saved)
