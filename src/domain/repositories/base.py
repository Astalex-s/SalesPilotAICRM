"""
BaseRepository — абстрактная база для всех интерфейсов репозиториев домена.
Чистый Python ABC. Без ORM, без инфраструктурных импортов.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Минимальный CRUD-контракт, который обязаны реализовать все репозитории домена."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Возвращает сущность по ID или None, если не найдена."""
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Сохраняет новую или обновлённую сущность и возвращает её."""
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """Удаляет сущность по ID."""
        ...
