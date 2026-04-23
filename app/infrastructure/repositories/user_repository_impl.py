from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.role import Role
from app.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one_or_none()
        if model is None:
            model = self._to_model(user)
            self._session.add(model)
        else:
            model.email = str(user.email)
            model.full_name = user.full_name
            model.hashed_password = user.hashed_password
            model.role = user.role
            model.is_active = user.is_active
            model.bio = user.bio
            model.updated_at = user.updated_at
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_all(self, offset: int = 0, limit: int = 20) -> list[User]:
        result = await self._session.execute(select(UserModel).offset(offset).limit(limit))
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            role=Role(model.role),
            is_active=model.is_active,
            bio=model.bio,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            full_name=entity.full_name,
            hashed_password=entity.hashed_password,
            role=entity.role,
            is_active=entity.is_active,
            bio=entity.bio,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
