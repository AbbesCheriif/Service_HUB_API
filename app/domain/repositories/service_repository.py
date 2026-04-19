from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.service import Service


class ServiceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, service_id: UUID) -> Optional[Service]: ...

    @abstractmethod
    async def get_by_provider(self, provider_id: UUID) -> list[Service]: ...

    @abstractmethod
    async def save(self, service: Service) -> Service: ...

    @abstractmethod
    async def delete(self, service_id: UUID) -> None: ...

    @abstractmethod
    async def list_active(self, offset: int = 0, limit: int = 20) -> list[Service]: ...
