"""
SqlLeadRepository — реализация ILeadRepository на SQLAlchemy 2.0 async.
Только I/O: SQL-запросы и маппинг. Никакой бизнес-логики.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.lead import Lead
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.enums import LeadStatus
from src.infrastructure.database.models.lead_model import LeadModel


class SqlLeadRepository(ILeadRepository):
    """Реализация ILeadRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        # Сессия — единственная инфраструктурная зависимость
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Lead | None:
        """Возвращает лид по UUID или None."""
        row = await self._session.get(LeadModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: Lead) -> Lead:
        """Выполняет upsert лида и возвращает актуальное состояние."""
        orm = LeadModel.from_entity(entity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, entity_id: UUID) -> None:
        """Удаляет лид по UUID."""
        row = await self._session.get(LeadModel, entity_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_by_owner(self, owner_id: UUID) -> list[Lead]:
        """Возвращает все лиды указанного пользователя."""
        stmt = select(LeadModel).where(LeadModel.owner_id == owner_id)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_status(self, status: LeadStatus) -> list[Lead]:
        """Возвращает все лиды с указанным статусом."""
        stmt = select(LeadModel).where(LeadModel.status == status)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_email(self, email: str) -> Lead | None:
        """Возвращает лид по e-mail (уникальный индекс) или None."""
        stmt = select(LeadModel).where(LeadModel.email == email).limit(1)
        rows = await self._session.scalars(stmt)
        row = rows.first()
        return row.to_entity() if row is not None else None
