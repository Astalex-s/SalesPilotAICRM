"""
SqlMeetingRepository — реализация IMeetingRepository на SQLAlchemy 2.0 async.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.meeting import Meeting
from src.domain.repositories.meeting_repository import IMeetingRepository
from src.domain.value_objects.enums import MeetingStatus
from src.infrastructure.database.models.meeting_model import MeetingModel


class SqlMeetingRepository(IMeetingRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, meeting_id: UUID) -> Meeting | None:
        row = await self._session.get(MeetingModel, meeting_id)
        return row.to_entity() if row else None

    async def save(self, meeting: Meeting) -> Meeting:
        orm = MeetingModel.from_entity(meeting)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, meeting_id: UUID) -> None:
        row = await self._session.get(MeetingModel, meeting_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_all(
        self,
        created_by_id: UUID | None = None,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        status: MeetingStatus | None = None,
    ) -> list[Meeting]:
        stmt = select(MeetingModel)
        if created_by_id is not None:
            stmt = stmt.where(MeetingModel.created_by_id == created_by_id)
        if lead_id is not None:
            stmt = stmt.where(MeetingModel.lead_id == lead_id)
        if deal_id is not None:
            stmt = stmt.where(MeetingModel.deal_id == deal_id)
        if from_date is not None:
            stmt = stmt.where(MeetingModel.start_time >= from_date)
        if to_date is not None:
            stmt = stmt.where(MeetingModel.start_time <= to_date)
        if status is not None:
            stmt = stmt.where(MeetingModel.status == status)
        stmt = stmt.order_by(MeetingModel.start_time.asc())
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
