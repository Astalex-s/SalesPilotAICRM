"""
SqlGdprAuditRepository — реализация IGdprAuditRepository на SQLAlchemy 2.0 async.
Append-only журнал: delete() выбрасывает NotImplementedError — записи аудита неизменяемы.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository
from src.domain.value_objects.enums import GdprEventType
from src.infrastructure.database.models.gdpr_audit_model import GdprAuditModel


class SqlGdprAuditRepository(IGdprAuditRepository):
    """Реализация IGdprAuditRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> GdprAuditEntry | None:
        """Возвращает запись аудита по UUID или None."""
        row = await self._session.get(GdprAuditModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: GdprAuditEntry) -> GdprAuditEntry:
        """Добавляет новую запись в append-only журнал аудита."""
        orm = GdprAuditModel.from_entity(entity)
        self._session.add(orm)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> None:
        """Удаление запрещено — журнал аудита GDPR является неизменяемым (Art. 30)."""
        raise NotImplementedError(
            "Записи журнала аудита GDPR являются append-only — удаление запрещено."
        )

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[GdprAuditEntry]:
        """Возвращает записи журнала от новых к старым с пагинацией."""
        stmt = (
            select(GdprAuditModel)
            .order_by(GdprAuditModel.performed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_event_type(
        self,
        event_type: GdprEventType,
    ) -> list[GdprAuditEntry]:
        """Возвращает все записи указанного типа события."""
        stmt = (
            select(GdprAuditModel)
            .where(GdprAuditModel.event_type == event_type)
            .order_by(GdprAuditModel.performed_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_target(
        self,
        target_type: str,
        target_id: UUID,
    ) -> list[GdprAuditEntry]:
        """Возвращает историю GDPR-событий для конкретного субъекта."""
        stmt = (
            select(GdprAuditModel)
            .where(
                GdprAuditModel.target_type == target_type,
                GdprAuditModel.target_id == target_id,
            )
            .order_by(GdprAuditModel.performed_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_since(self, since: datetime) -> list[GdprAuditEntry]:
        """Возвращает все записи после указанного момента времени."""
        stmt = (
            select(GdprAuditModel)
            .where(GdprAuditModel.performed_at >= since)
            .order_by(GdprAuditModel.performed_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
