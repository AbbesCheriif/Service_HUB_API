from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.dto.booking_dto import BookingCreateDTO
from app.application.use_cases.booking.create_booking import CreateBooking
from app.domain.exceptions import BookingConflict, ServiceNotFound


@pytest.mark.asyncio
async def test_create_booking_success(mock_uow, sample_service, sample_booking):
    mock_uow.services.get_by_id.return_value = sample_service
    mock_uow.bookings.has_conflict.return_value = False
    mock_uow.bookings.save.return_value = sample_booking

    use_case = CreateBooking(uow=mock_uow)
    dto = BookingCreateDTO(
        service_id=sample_service.id,
        scheduled_at=datetime(2025, 6, 1, 10, 0, tzinfo=UTC),
    )
    client_id = uuid4()

    result = await use_case.execute(dto, client_id=client_id)

    assert result.service_id == sample_booking.service_id
    assert result.total_price == sample_service.price
    mock_uow.bookings.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_booking_service_not_found(mock_uow):
    mock_uow.services.get_by_id.return_value = None

    use_case = CreateBooking(uow=mock_uow)
    dto = BookingCreateDTO(
        service_id=uuid4(),
        scheduled_at=datetime(2025, 6, 1, 10, 0, tzinfo=UTC),
    )

    with pytest.raises(ServiceNotFound):
        await use_case.execute(dto, client_id=uuid4())

    mock_uow.bookings.save.assert_not_called()


@pytest.mark.asyncio
async def test_create_booking_conflict(mock_uow, sample_service):
    mock_uow.services.get_by_id.return_value = sample_service
    mock_uow.bookings.has_conflict.return_value = True

    use_case = CreateBooking(uow=mock_uow)
    dto = BookingCreateDTO(
        service_id=sample_service.id,
        scheduled_at=datetime(2025, 6, 1, 10, 0, tzinfo=UTC),
    )

    with pytest.raises(BookingConflict):
        await use_case.execute(dto, client_id=uuid4())

    mock_uow.bookings.save.assert_not_called()


@pytest.mark.asyncio
async def test_create_booking_no_background_tasks(mock_uow, sample_service, sample_booking):
    mock_uow.services.get_by_id.return_value = sample_service
    mock_uow.bookings.has_conflict.return_value = False
    mock_uow.bookings.save.return_value = sample_booking

    use_case = CreateBooking(uow=mock_uow)
    dto = BookingCreateDTO(
        service_id=sample_service.id,
        scheduled_at=datetime(2025, 6, 1, 10, 0, tzinfo=UTC),
    )

    result = await use_case.execute(dto, client_id=uuid4(), background_tasks=None)

    assert result is not None
