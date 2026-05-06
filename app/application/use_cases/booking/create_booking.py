from typing import Optional
from uuid import UUID

from fastapi import BackgroundTasks

from app.application.dto.booking_dto import BookingCreateDTO, BookingReadDTO
from app.application.dto.mappers import booking_to_dto, dto_to_booking
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import BookingConflict, ServiceNotFound
from app.infrastructure.background.booking_notification_task import notify_provider_new_booking
from app.infrastructure.background.stats_task import schedule_provider_stats_recalculation


class CreateBooking:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        dto: BookingCreateDTO,
        client_id: UUID,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BookingReadDTO:
        async with self._uow:
            service = await self._uow.services.get_by_id(dto.service_id)
            if not service:
                raise ServiceNotFound(str(dto.service_id))
            if await self._uow.bookings.has_conflict(dto.service_id, dto.scheduled_at):
                raise BookingConflict()
            booking = dto_to_booking(
                dto,
                client_id=client_id,
                provider_id=service.provider_id,
                total_price=service.price,
            )
            saved = await self._uow.bookings.save(booking)

        if background_tasks is not None:
            notify_provider_new_booking(
                provider_email="",
                booking_id=saved.id,
                service_name=service.title,
                background_tasks=background_tasks,
            )
            schedule_provider_stats_recalculation(
                provider_id=service.provider_id,
                background_tasks=background_tasks,
            )

        return booking_to_dto(saved)
