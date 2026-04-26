from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_session
from app.api.schemas.auth_schema import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.application.dto.user_dto import UserCreateDTO, UserReadDTO
from app.application.use_cases.auth.login import Login
from app.application.use_cases.auth.register import Register
from app.domain.exceptions import InvalidCredentials
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.password_service import PasswordService
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserReadDTO, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = Register(uow=uow, password_service=PasswordService())
    dto = UserCreateDTO(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
    )
    return await use_case.execute(dto)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = Login(uow=uow, password_service=PasswordService(), jwt_service=JWTService())
    result = await use_case.execute(payload.email, payload.password)
    return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    jwt_service = JWTService()
    token_data = jwt_service.decode_token(payload.refresh_token)
    if token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = token_data.get("sub", "")
    repo = SQLAlchemyUserRepository(session)
    user = await repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    access_token = jwt_service.create_access_token(str(user.id), user.role.value)
    return TokenResponse(access_token=access_token, refresh_token=payload.refresh_token)
