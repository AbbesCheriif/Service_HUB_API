from dataclasses import dataclass

from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import InvalidCredentials
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.password_service import PasswordService


@dataclass
class TokenDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Login:
    def __init__(self, uow: UnitOfWork, password_service: PasswordService, jwt_service: JWTService) -> None:
        self._uow = uow
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def execute(self, email: str, password: str) -> TokenDTO:
        async with self._uow:
            user = await self._uow.users.get_by_email(email)
            if not user:
                raise InvalidCredentials()
            if not self._password_service.verify(password, user.hashed_password):
                raise InvalidCredentials()
            access_token = self._jwt_service.create_access_token(str(user.id), user.role.value)
            refresh_token = self._jwt_service.create_refresh_token(str(user.id))
            return TokenDTO(access_token=access_token, refresh_token=refresh_token)
