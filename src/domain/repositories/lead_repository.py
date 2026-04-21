"""
ILeadRepository — интерфейс репозитория домена для сущности Lead.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.lead import Lead
from src.domain.repositories.base import BaseRepository
from src.domain.value_objects.enums import LeadStatus


class ILeadRepository(BaseRepository[Lead]):
    """Контракт для операций с хранилищем лидов."""

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> list[Lead]:
        """Возвращает все лиды, принадлежащие указанному пользователю."""
        ...

    @abstractmethod
    async def find_by_status(self, status: LeadStatus) -> list[Lead]:
        """Возвращает все лиды с указанным статусом."""
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Lead | None:
        """Возвращает лид по адресу e-mail или None."""
        ...

    @abstractmethod
    async def find_all(self) -> list[Lead]:
        """Возвращает все лиды в системе (используется администратором)."""
        ...
