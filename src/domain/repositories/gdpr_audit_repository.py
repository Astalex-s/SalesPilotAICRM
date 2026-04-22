"""
IGdprAuditRepository — интерфейс репозитория журнала аудита GDPR.
Append-only: удаление записей аудита запрещено по требованиям GDPR.
"""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.base import BaseRepository
from src.domain.value_objects.enums import GdprEventType


class IGdprAuditRepository(BaseRepository[GdprAuditEntry]):
    """Контракт для операций с журналом аудита GDPR.

    delete() в конкретных реализациях обязан выбрасывать NotImplementedError —
    журнал аудита должен храниться не менее 3 лет (GDPR Art. 30).
    """

    @abstractmethod
    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[GdprAuditEntry]:
        """Возвращает записи журнала от новых к старым с пагинацией."""
        ...

    @abstractmethod
    async def find_by_event_type(
        self,
        event_type: GdprEventType,
    ) -> list[GdprAuditEntry]:
        """Возвращает все записи указанного типа события."""
        ...

    @abstractmethod
    async def find_by_target(
        self,
        target_type: str,
        target_id: UUID,
    ) -> list[GdprAuditEntry]:
        """Возвращает историю GDPR-событий для конкретного субъекта."""
        ...

    @abstractmethod
    async def find_since(self, since: datetime) -> list[GdprAuditEntry]:
        """Возвращает все записи после указанного момента времени."""
        ...
