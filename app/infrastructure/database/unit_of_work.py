from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.repositories.booking_repository_impl import SQLAlchemyBookingRepository
from app.infrastructure.repositories.service_repository_impl import SQLAlchemyServiceRepository
from app.infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.users = SQLAlchemyUserRepository(self._session)
        self.services = SQLAlchemyServiceRepository(self._session)
        self.bookings = SQLAlchemyBookingRepository(self._session)
        return self

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
