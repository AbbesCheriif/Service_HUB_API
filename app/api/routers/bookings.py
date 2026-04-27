from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_role
from app.api.dependencies.database import get_session
from app.api.schemas.booking_schema import BookingCreateRequest, BookingResponse
from app.api.schemas.pagination import PageParams, PaginatedResponse
from app.application.dto.booking_dto import BookingCreateDTO
from app.application.use_cases.booking.accept_booking import AcceptBooking
from app.application.use_cases.booking.cancel_booking import CancelBooking
from app.application.use_cases.booking.create_booking import CreateBooking
from app.domain.entities.user import User
from app.domain.exceptions import BookingNotFound, PermissionDenied
from app.domain.value_objects.role import Role
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(
    payload: BookingCreateRequest,
    current_user: Annotated[User, Depends(require_role(Role.CLIENT))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateBooking(uow=uow)
    dto = BookingCreateDTO(**payload.model_dump())
    return await use_case.execute(dto, client_id=current_user.id)


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def list_bookings(
    params: Annotated[PageParams, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        if current_user.role == Role.PROVIDER:
            all_items = await uow.bookings.get_by_provider(current_user.id)
        else:
            all_items = await uow.bookings.get_by_client(current_user.id)
    page_items = all_items[params.offset : params.offset + params.size]
    has_next = len(all_items) > params.offset + params.size
    return PaginatedResponse(items=page_items, page=params.page, size=params.size, has_next=has_next)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        booking = await uow.bookings.get_by_id(booking_id)
    if not booking:
        raise BookingNotFound(str(booking_id))
    if current_user.role != Role.ADMIN and current_user.id not in (booking.client_id, booking.provider_id):
        raise PermissionDenied("access denied")
    return booking


@router.post("/{booking_id}/accept", response_model=BookingResponse)
async def accept_booking(
    booking_id: UUID,
    current_user: Annotated[User, Depends(require_role(Role.PROVIDER, Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = AcceptBooking(uow=uow)
    return await use_case.execute(booking_id, provider_id=current_user.id)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CancelBooking(uow=uow)
    return await use_case.execute(booking_id, requester_id=current_user.id)
