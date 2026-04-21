from uuid import UUID

from app.application.dto.booking_dto import BookingCreateDTO, BookingReadDTO
from app.application.dto.mappers import booking_to_dto, dto_to_booking
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import BookingConflict, ServiceNotFound


class CreateBooking:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: BookingCreateDTO, client_id: UUID) -> BookingReadDTO:
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
            return booking_to_dto(saved)
