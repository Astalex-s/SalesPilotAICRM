"""
IStageRepository — интерфейс репозитория домена для сущности Stage.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.stage import Stage
from src.domain.repositories.base import BaseRepository


class IStageRepository(BaseRepository[Stage]):
    """Контракт для операций с хранилищем этапов."""

    @abstractmethod
    async def find_by_pipeline(self, pipeline_id: UUID) -> list[Stage]:
        """Возвращает все этапы воронки, упорядоченные по полю order."""
        ...
