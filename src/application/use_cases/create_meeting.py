from __future__ import annotations

from uuid import UUID

from src.application.dtos.meeting_dtos import CreateMeetingInput, MeetingOutput
from src.domain.entities.meeting import Meeting
from src.domain.repositories.meeting_repository import IMeetingRepository


class CreateMeetingUseCase:
    def __init__(self, meeting_repo: IMeetingRepository) -> None:
        self._repo = meeting_repo

    async def execute(self, data: CreateMeetingInput, created_by_id: UUID) -> MeetingOutput:
        meeting = Meeting.create(
            title=data.title,
            start_time=data.start_time,
            created_by_id=created_by_id,
            description=data.description,
            end_time=data.end_time,
            location=data.location,
            lead_id=data.lead_id,
            deal_id=data.deal_id,
        )
        saved = await self._repo.save(meeting)
        return MeetingOutput.from_entity(saved)
