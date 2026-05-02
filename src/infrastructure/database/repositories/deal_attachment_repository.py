"""
SqlDealAttachmentRepository — реализация IDealAttachmentRepository на SQLAlchemy.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.deal_attachment import DealAttachment
from src.domain.repositories.deal_attachment_repository import IDealAttachmentRepository
from src.infrastructure.database.models.deal_attachment_model import DealAttachmentModel


class SqlDealAttachmentRepository(IDealAttachmentRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> DealAttachment | None:
        row = await self._session.get(DealAttachmentModel, entity_id)
        return row.to_entity() if row else None

    async def save(self, entity: DealAttachment) -> DealAttachment:
        orm = DealAttachmentModel.from_entity(entity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, entity_id: UUID) -> None:
        row = await self._session.get(DealAttachmentModel, entity_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    async def find_by_deal(self, deal_id: UUID) -> list[DealAttachment]:
        stmt = (
            select(DealAttachmentModel)
            .where(DealAttachmentModel.deal_id == deal_id)
            .order_by(DealAttachmentModel.created_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
