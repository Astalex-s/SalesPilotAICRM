"""
MeetingModel — ORM-модель таблицы meetings (CRM-встречи/события).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.meeting import Meeting
from src.domain.value_objects.enums import MeetingStatus
from src.infrastructure.database.base import Base


class MeetingModel(Base):
    __tablename__ = "meetings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lead_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    deal_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    created_by_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[MeetingStatus] = mapped_column(
        SAEnum(MeetingStatus, name="meetingstatus"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_entity(self) -> Meeting:
        return Meeting(
            id=self.id,
            title=self.title,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            location=self.location,
            lead_id=self.lead_id,
            deal_id=self.deal_id,
            created_by_id=self.created_by_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, meeting: Meeting) -> MeetingModel:
        return cls(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            location=meeting.location,
            lead_id=meeting.lead_id,
            deal_id=meeting.deal_id,
            created_by_id=meeting.created_by_id,
            status=meeting.status,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at,
        )
