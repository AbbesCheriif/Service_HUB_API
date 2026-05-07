from uuid import UUID

from fastapi import BackgroundTasks

from app.application.services.notification_service import NotificationService
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class EmailNotificationService(NotificationService):
    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self._tasks = background_tasks

    async def send_email(self, to: str, subject: str, body: str) -> None:
        self._tasks.add_task(self._mock_smtp_send, to, subject, body)

    async def notify_booking_confirmation(
        self, booking_id: UUID, client_email: str
    ) -> None:
        await self.send_email(
            to=client_email,
            subject="Booking Confirmed",
            body=f"Your booking {booking_id} has been confirmed.",
        )

    async def notify_booking_cancellation(
        self, booking_id: UUID, client_email: str
    ) -> None:
        await self.send_email(
            to=client_email,
            subject="Booking Cancelled",
            body=f"Your booking {booking_id} has been cancelled.",
        )

    @staticmethod
    def _mock_smtp_send(to: str, subject: str, body: str) -> None:
        logger.info("mock_email_sent", to=to, subject=subject, body=body)
