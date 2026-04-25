from app.application.dto.mappers import dto_to_user, user_to_dto
from app.application.dto.user_dto import UserCreateDTO, UserReadDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserAlreadyExists
from app.infrastructure.auth.password_service import PasswordService


class Register:
    def __init__(self, uow: UnitOfWork, password_service: PasswordService) -> None:
        self._uow = uow
        self._password_service = password_service

    async def execute(self, dto: UserCreateDTO) -> UserReadDTO:
        async with self._uow:
            existing = await self._uow.users.get_by_email(dto.email)
            if existing:
                raise UserAlreadyExists(dto.email)
            hashed_password = self._password_service.hash(dto.password)
            user = dto_to_user(dto, hashed_password=hashed_password)
            saved = await self._uow.users.save(user)
            return user_to_dto(saved)
