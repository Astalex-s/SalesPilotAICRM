"""
IUserRepository — интерфейс репозитория домена для сущности User.
"""
from __future__ import annotations

from abc import abstractmethod

from src.domain.entities.user import User
from src.domain.repositories.base import BaseRepository


class IUserRepository(BaseRepository[User]):
    """Контракт для операций с хранилищем пользователей."""

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Возвращает пользователя по e-mail или None."""
        ...

    @abstractmethod
    async def find_active(self) -> list[User]:
        """Возвращает всех активных пользователей."""
        ...
