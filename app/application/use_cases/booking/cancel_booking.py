from uuid import UUID

from app.application.dto.booking_dto import BookingReadDTO
from app.application.dto.mappers import booking_to_dto
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import BookingNotFound, InvalidBookingTransition, PermissionDenied
from app.domain.value_objects.booking_status import BookingStatus


class CancelBooking:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, booking_id: UUID, requester_id: UUID) -> BookingReadDTO:
        async with self._uow:
            booking = await self._uow.bookings.get_by_id(booking_id)
            if not booking:
                raise BookingNotFound(str(booking_id))
            if requester_id not in (booking.client_id, booking.provider_id):
                raise PermissionDenied("only the client or provider can cancel this booking")
            if booking.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
                raise InvalidBookingTransition(booking.status.value, BookingStatus.CANCELLED.value)
            booking.status = BookingStatus.CANCELLED
            saved = await self._uow.bookings.save(booking)
            return booking_to_dto(saved)
