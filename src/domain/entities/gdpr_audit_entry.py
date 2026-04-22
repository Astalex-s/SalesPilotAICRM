"""
GdprAuditEntry — доменная сущность записи журнала GDPR.
Иммутабельная запись: фиксирует каждое действие по запросу субъекта данных.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.enums import GdprEventType


@dataclass(frozen=True)
class GdprAuditEntry:
    """Запись журнала аудита GDPR.

    Инварианты:
    - frozen=True — записи неизменяемы после создания
    - performed_at всегда UTC
    """

    id: UUID
    event_type: GdprEventType
    target_type: str        # "user" | "lead"
    target_id: UUID
    summary: str
    performed_at: datetime
    performed_by_id: UUID | None = None   # None = системное действие

    @classmethod
    def create(
        cls,
        event_type: GdprEventType,
        target_type: str,
        target_id: UUID,
        summary: str,
        performed_by_id: UUID | None = None,
    ) -> GdprAuditEntry:
        """Фабричный метод — генерирует ID и проставляет текущий UTC-timestamp."""
        return cls(
            id=uuid4(),
            event_type=event_type,
            target_type=target_type,
            target_id=target_id,
            summary=summary,
            performed_at=datetime.now(timezone.utc),
            performed_by_id=performed_by_id,
        )
