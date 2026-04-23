from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.service import Service
from app.domain.repositories.service_repository import ServiceRepository
from app.infrastructure.database.models.service_model import ServiceModel


class SQLAlchemyServiceRepository(ServiceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, service_id: UUID) -> Optional[Service]:
        result = await self._session.execute(select(ServiceModel).where(ServiceModel.id == service_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_provider(self, provider_id: UUID) -> list[Service]:
        result = await self._session.execute(
            select(ServiceModel).where(ServiceModel.provider_id == provider_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, service: Service) -> Service:
        result = await self._session.execute(select(ServiceModel).where(ServiceModel.id == service.id))
        model = result.scalar_one_or_none()
        if model is None:
            model = self._to_model(service)
            self._session.add(model)
        else:
            model.title = service.title
            model.description = service.description
            model.price = service.price
            model.duration_minutes = service.duration_minutes
            model.is_active = service.is_active
            model.category = service.category
            model.average_rating = service.average_rating
            model.total_reviews = service.total_reviews
            model.updated_at = service.updated_at
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, service_id: UUID) -> None:
        result = await self._session.execute(select(ServiceModel).where(ServiceModel.id == service_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_active(self, offset: int = 0, limit: int = 20) -> list[Service]:
        result = await self._session.execute(
            select(ServiceModel)
            .where(ServiceModel.is_active == True)  # noqa: E712
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            provider_id=model.provider_id,
            title=model.title,
            description=model.description,
            price=model.price,
            duration_minutes=model.duration_minutes,
            is_active=model.is_active,
            category=model.category,
            average_rating=model.average_rating,
            total_reviews=model.total_reviews,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Service) -> ServiceModel:
        return ServiceModel(
            id=entity.id,
            provider_id=entity.provider_id,
            title=entity.title,
            description=entity.description,
            price=entity.price,
            duration_minutes=entity.duration_minutes,
            is_active=entity.is_active,
            category=entity.category,
            average_rating=entity.average_rating,
            total_reviews=entity.total_reviews,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
