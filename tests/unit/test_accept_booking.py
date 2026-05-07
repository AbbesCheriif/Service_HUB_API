from uuid import uuid4

import pytest

from app.application.use_cases.booking.accept_booking import AcceptBooking
from app.domain.exceptions import (
    BookingNotFound,
    InvalidBookingTransition,
    PermissionDenied,
)
from app.domain.value_objects.booking_status import BookingStatus


@pytest.mark.asyncio
async def test_accept_booking_success(mock_uow, sample_booking):
    provider_id = sample_booking.provider_id
    sample_booking.status = BookingStatus.PENDING
    mock_uow.bookings.get_by_id.return_value = sample_booking
    mock_uow.bookings.save.return_value = sample_booking

    use_case = AcceptBooking(uow=mock_uow)
    result = await use_case.execute(sample_booking.id, provider_id=provider_id)

    assert result.status == BookingStatus.CONFIRMED
    mock_uow.bookings.save.assert_called_once()


@pytest.mark.asyncio
async def test_accept_booking_not_found(mock_uow):
    mock_uow.bookings.get_by_id.return_value = None

    use_case = AcceptBooking(uow=mock_uow)

    with pytest.raises(BookingNotFound):
        await use_case.execute(uuid4(), provider_id=uuid4())


@pytest.mark.asyncio
async def test_accept_booking_wrong_provider(mock_uow, sample_booking):
    sample_booking.status = BookingStatus.PENDING
    mock_uow.bookings.get_by_id.return_value = sample_booking

    use_case = AcceptBooking(uow=mock_uow)
    wrong_provider_id = uuid4()

    with pytest.raises(PermissionDenied):
        await use_case.execute(sample_booking.id, provider_id=wrong_provider_id)

    mock_uow.bookings.save.assert_not_called()


@pytest.mark.asyncio
async def test_accept_booking_invalid_transition(mock_uow, sample_booking):
    sample_booking.status = BookingStatus.CONFIRMED
    mock_uow.bookings.get_by_id.return_value = sample_booking

    use_case = AcceptBooking(uow=mock_uow)

    with pytest.raises(InvalidBookingTransition):
        await use_case.execute(sample_booking.id, provider_id=sample_booking.provider_id)

    mock_uow.bookings.save.assert_not_called()


@pytest.mark.asyncio
async def test_accept_booking_cancelled_raises_transition_error(mock_uow, sample_booking):
    sample_booking.status = BookingStatus.CANCELLED
    mock_uow.bookings.get_by_id.return_value = sample_booking

    use_case = AcceptBooking(uow=mock_uow)

    with pytest.raises(InvalidBookingTransition):
        await use_case.execute(sample_booking.id, provider_id=sample_booking.provider_id)
