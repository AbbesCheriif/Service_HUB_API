from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.entities.booking import Booking


class BookingRepository(ABC):
    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Optional[Booking]: ...

    @abstractmethod
    async def get_by_client(self, client_id: UUID) -> list[Booking]: ...

    @abstractmethod
    async def get_by_provider(self, provider_id: UUID) -> list[Booking]: ...

    @abstractmethod
    async def get_by_service(self, service_id: UUID) -> list[Booking]: ...

    @abstractmethod
    async def save(self, booking: Booking) -> Booking: ...

    @abstractmethod
    async def delete(self, booking_id: UUID) -> None: ...

    @abstractmethod
    async def has_conflict(self, service_id: UUID, scheduled_at: datetime) -> bool: ...
