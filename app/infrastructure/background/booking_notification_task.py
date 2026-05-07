from uuid import UUID

from fastapi import BackgroundTasks

from app.core.logging.logger import get_logger

logger = get_logger(__name__)


def notify_provider_new_booking(
    provider_email: str,
    booking_id: UUID,
    service_name: str,
    background_tasks: BackgroundTasks,
) -> None:
    background_tasks.add_task(
        _send_provider_new_booking,
        provider_email,
        booking_id,
        service_name,
    )


def notify_client_booking_accepted(
    client_email: str,
    booking_id: UUID,
    background_tasks: BackgroundTasks,
) -> None:
    background_tasks.add_task(
        _send_client_booking_accepted,
        client_email,
        booking_id,
    )


def notify_client_booking_cancelled(
    client_email: str,
    booking_id: UUID,
    background_tasks: BackgroundTasks,
) -> None:
    background_tasks.add_task(
        _send_client_booking_cancelled,
        client_email,
        booking_id,
    )


def _send_provider_new_booking(
    provider_email: str, booking_id: UUID, service_name: str
) -> None:
    logger.info(
        "mock_provider_new_booking",
        to=provider_email,
        booking_id=str(booking_id),
        service=service_name,
    )


def _send_client_booking_accepted(client_email: str, booking_id: UUID) -> None:
    logger.info(
        "mock_client_booking_accepted",
        to=client_email,
        booking_id=str(booking_id),
    )


def _send_client_booking_cancelled(client_email: str, booking_id: UUID) -> None:
    logger.info(
        "mock_client_booking_cancelled",
        to=client_email,
        booking_id=str(booking_id),
    )
