from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from app.domain.repositories.booking_repository import BookingRepository
from app.domain.repositories.service_repository import ServiceRepository
from app.domain.repositories.user_repository import UserRepository


class UnitOfWork(ABC):
    users: UserRepository
    services: ServiceRepository
    bookings: BookingRepository

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
