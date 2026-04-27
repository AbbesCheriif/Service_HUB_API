from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import require_role
from app.api.dependencies.database import get_session
from app.domain.entities.user import User
from app.domain.exceptions import UserNotFound
from app.domain.value_objects.role import Role
from app.infrastructure.database.models.booking_model import BookingModel
from app.infrastructure.database.models.service_model import ServiceModel
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    _: Annotated[User, Depends(require_role(Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user_count = (await session.execute(select(func.count()).select_from(UserModel))).scalar()
    service_count = (await session.execute(select(func.count()).select_from(ServiceModel))).scalar()
    booking_count = (await session.execute(select(func.count()).select_from(BookingModel))).scalar()
    return {
        "users": user_count,
        "services": service_count,
        "bookings": booking_count,
    }


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    _: Annotated[User, Depends(require_role(Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))
        await uow.users.delete(user_id)
        await uow.commit()
