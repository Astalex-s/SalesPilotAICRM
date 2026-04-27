"""
SqlUserRepository — реализация IUserRepository поверх SQLAlchemy.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.database.models.user_model import UserModel


class SqlUserRepository(IUserRepository):
    """Реализация репозитория пользователей на основе SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> User | None:
        return await self.find_by_id(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def save(self, entity: User) -> User:
        raise NotImplementedError("Используйте save_with_hash для пользователей.")

    async def save_with_hash(self, user: User, password_hash: str) -> User:
        """Сохраняет пользователя вместе с хэшем пароля."""
        model = UserModel.from_entity(user, password_hash)
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def find_by_id(self, entity_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_email_with_hash(self, email: str) -> tuple[User, str] | None:
        """Возвращает пользователя и хэш пароля (только для аутентификации)."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity(), model.password_hash

    async def find_active(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.is_active == True).order_by(UserModel.created_at)  # noqa: E712
        )
        return [row.to_entity() for row in result.scalars().all()]

    async def find_all(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel).order_by(UserModel.created_at)
        )
        return [row.to_entity() for row in result.scalars().all()]

    async def update_role(self, user_id: UUID, role: str) -> User | None:
        """Обновляет роль пользователя напрямую в БД."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.role = role  # type: ignore[assignment]
        await self._session.flush()
        return model.to_entity()
