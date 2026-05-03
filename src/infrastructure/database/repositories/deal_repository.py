"""
SqlDealRepository — реализация IDealRepository на SQLAlchemy 2.0 async.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.deal import Deal
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.value_objects.enums import DealStatus
from src.infrastructure.database.models.deal_model import DealModel


class SqlDealRepository(IDealRepository):
    """Реализация IDealRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Deal | None:
        """Возвращает сделку по UUID или None."""
        row = await self._session.get(DealModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: Deal) -> Deal:
        """Выполняет upsert сделки и возвращает актуальное состояние."""
        orm = DealModel.from_entity(entity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, entity_id: UUID) -> None:
        """Удаляет сделку по UUID."""
        row = await self._session.get(DealModel, entity_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_all(self) -> list[Deal]:
        """Возвращает все сделки (для аналитических запросов)."""
        stmt = select(DealModel)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_owner(self, owner_id: UUID) -> list[Deal]:
        """Возвращает все сделки указанного пользователя."""
        stmt = select(DealModel).where(DealModel.owner_id == owner_id)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_pipeline(self, pipeline_id: UUID) -> list[Deal]:
        """Возвращает все сделки в указанной воронке."""
        stmt = select(DealModel).where(DealModel.pipeline_id == pipeline_id)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_stage(self, stage_id: UUID) -> list[Deal]:
        """Возвращает все сделки на указанном этапе."""
        stmt = select(DealModel).where(DealModel.stage_id == stage_id)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_status(self, status: DealStatus) -> list[Deal]:
        """Возвращает все сделки с указанным статусом."""
        stmt = select(DealModel).where(DealModel.status == status)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_source_lead(self, lead_id: UUID) -> Deal | None:
        """Возвращает сделку, созданную из указанного лида, или None."""
        stmt = (
            select(DealModel)
            .where(DealModel.source_lead_id == lead_id)
            .limit(1)
        )
        rows = await self._session.scalars(stmt)
        row = rows.first()
        return row.to_entity() if row is not None else None

    async def find_overdue(self, now: datetime) -> list[Deal]:
        """Возвращает открытые сделки с просроченным expected_close_date."""
        stmt = (
            select(DealModel)
            .where(
                DealModel.status == DealStatus.OPEN,
                DealModel.expected_close_date.is_not(None),
                DealModel.expected_close_date < now,
            )
            .order_by(DealModel.expected_close_date)
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
