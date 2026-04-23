from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.booking import Booking
from app.domain.repositories.booking_repository import BookingRepository
from app.domain.value_objects.booking_status import BookingStatus
from app.infrastructure.database.models.booking_model import BookingModel


class SQLAlchemyBookingRepository(BookingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        result = await self._session.execute(select(BookingModel).where(BookingModel.id == booking_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_client(self, client_id: UUID) -> list[Booking]:
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.client_id == client_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_provider(self, provider_id: UUID) -> list[Booking]:
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.provider_id == provider_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_service(self, service_id: UUID) -> list[Booking]:
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.service_id == service_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, booking: Booking) -> Booking:
        result = await self._session.execute(select(BookingModel).where(BookingModel.id == booking.id))
        model = result.scalar_one_or_none()
        if model is None:
            model = self._to_model(booking)
            self._session.add(model)
        else:
            model.status = booking.status
            model.notes = booking.notes
            model.total_price = booking.total_price
            model.scheduled_at = booking.scheduled_at
            model.updated_at = booking.updated_at
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, booking_id: UUID) -> None:
        result = await self._session.execute(select(BookingModel).where(BookingModel.id == booking_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def has_conflict(self, service_id: UUID, scheduled_at: datetime) -> bool:
        window = timedelta(hours=1)
        result = await self._session.execute(
            select(BookingModel).where(
                and_(
                    BookingModel.service_id == service_id,
                    BookingModel.status != BookingStatus.CANCELLED,
                    BookingModel.scheduled_at >= scheduled_at - window,
                    BookingModel.scheduled_at < scheduled_at + window,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: BookingModel) -> Booking:
        return Booking(
            id=model.id,
            client_id=model.client_id,
            service_id=model.service_id,
            provider_id=model.provider_id,
            scheduled_at=model.scheduled_at,
            status=BookingStatus(model.status),
            notes=model.notes,
            total_price=model.total_price,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Booking) -> BookingModel:
        return BookingModel(
            id=entity.id,
            client_id=entity.client_id,
            service_id=entity.service_id,
            provider_id=entity.provider_id,
            scheduled_at=entity.scheduled_at,
            status=entity.status,
            notes=entity.notes,
            total_price=entity.total_price,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
