"""
DTO-модели для встреч (Meetings).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.meeting import Meeting
from src.domain.value_objects.enums import MeetingStatus


class CreateMeetingInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    location: str | None = Field(None, max_length=255)
    lead_id: UUID | None = None
    deal_id: UUID | None = None


class UpdateMeetingInput(BaseModel):
    meeting_id: UUID
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    status: MeetingStatus | None = None


class ListMeetingsInput(BaseModel):
    lead_id: UUID | None = None
    deal_id: UUID | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    status: MeetingStatus | None = None


class MeetingOutput(BaseModel):
    id: UUID
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    location: str | None
    lead_id: UUID | None
    deal_id: UUID | None
    created_by_id: UUID
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_entity(cls, meeting: Meeting) -> MeetingOutput:
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
