from abc import ABC, abstractmethod
from uuid import UUID


class NotificationService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None: ...

    @abstractmethod
    async def notify_booking_confirmation(self, booking_id: UUID, client_email: str) -> None: ...

    @abstractmethod
    async def notify_booking_cancellation(self, booking_id: UUID, client_email: str) -> None: ...
