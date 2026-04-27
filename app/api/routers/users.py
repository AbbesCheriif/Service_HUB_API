from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_session
from app.api.schemas.user_schema import UserResponse
from app.application.use_cases.user.get_user import GetUser
from app.domain.entities.user import User
from app.domain.value_objects.role import Role
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    uow = SQLAlchemyUnitOfWork(session)
    use_case = GetUser(uow=uow)
    return await use_case.execute(user_id)
