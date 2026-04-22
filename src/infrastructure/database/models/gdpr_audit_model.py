"""
GdprAuditModel — ORM-модель таблицы gdpr_audit_log.
Append-only: строки только добавляются, удаление запрещено по GDPR Art. 30.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.value_objects.enums import GdprEventType
from src.infrastructure.database.base import Base


class GdprAuditModel(Base):
    """ORM-модель для таблицы gdpr_audit_log."""

    __tablename__ = "gdpr_audit_log"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    event_type: Mapped[GdprEventType] = mapped_column(
        SAEnum(GdprEventType, name="gdpreventtype"), nullable=False, index=True
    )
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    target_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    performed_by_id: Mapped[UUID | None] = mapped_column(nullable=True)

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> GdprAuditEntry:
        """Преобразует ORM-строку в доменную сущность GdprAuditEntry."""
        return GdprAuditEntry(
            id=self.id,
            event_type=self.event_type,
            target_type=self.target_type,
            target_id=self.target_id,
            summary=self.summary,
            performed_at=self.performed_at,
            performed_by_id=self.performed_by_id,
        )

    @classmethod
    def from_entity(cls, entry: GdprAuditEntry) -> GdprAuditModel:
        """Преобразует доменную сущность GdprAuditEntry в ORM-модель."""
        return cls(
            id=entry.id,
            event_type=entry.event_type,
            target_type=entry.target_type,
            target_id=entry.target_id,
            summary=entry.summary,
            performed_at=entry.performed_at,
            performed_by_id=entry.performed_by_id,
        )
