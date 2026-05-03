"""
IDealRepository — интерфейс репозитория домена для сущности Deal.
"""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.deal import Deal
from src.domain.repositories.base import BaseRepository
from src.domain.value_objects.enums import DealStatus


class IDealRepository(BaseRepository[Deal]):
    """Контракт для операций с хранилищем сделок."""

    @abstractmethod
    async def find_all(self) -> list[Deal]:
        """Возвращает все сделки в системе (используется в аналитике)."""
        ...

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> list[Deal]:
        """Возвращает все сделки указанного пользователя."""
        ...

    @abstractmethod
    async def find_by_pipeline(self, pipeline_id: UUID) -> list[Deal]:
        """Возвращает все сделки в указанной воронке."""
        ...

    @abstractmethod
    async def find_by_stage(self, stage_id: UUID) -> list[Deal]:
        """Возвращает все сделки на указанном этапе."""
        ...

    @abstractmethod
    async def find_by_status(self, status: DealStatus) -> list[Deal]:
        """Возвращает все сделки с указанным статусом."""
        ...

    @abstractmethod
    async def find_by_source_lead(self, lead_id: UUID) -> Deal | None:
        """Возвращает сделку, созданную из конкретного лида, или None."""
        ...

    @abstractmethod
    async def find_overdue(self, now: datetime) -> list[Deal]:
        """Возвращает открытые сделки, у которых expected_close_date < now."""
        ...
