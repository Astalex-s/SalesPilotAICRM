"""
IPipelineRepository — интерфейс репозитория домена для сущности Pipeline.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.pipeline import Pipeline
from src.domain.repositories.base import BaseRepository


class IPipelineRepository(BaseRepository[Pipeline]):
    """Контракт для операций с хранилищем воронок продаж."""

    @abstractmethod
    async def find_active(self) -> list[Pipeline]:
        """Возвращает все активные воронки."""
        ...

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> list[Pipeline]:
        """Возвращает все воронки, принадлежащие указанному пользователю."""
        ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Pipeline | None:
        """Возвращает воронку по точному названию или None."""
        ...
