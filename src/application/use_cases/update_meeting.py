from __future__ import annotations

from src.application.dtos.meeting_dtos import MeetingOutput, UpdateMeetingInput
from src.application.exceptions import MeetingNotFoundError
from src.domain.repositories.meeting_repository import IMeetingRepository


class UpdateMeetingUseCase:
    def __init__(self, meeting_repo: IMeetingRepository) -> None:
        self._repo = meeting_repo

    async def execute(self, data: UpdateMeetingInput) -> MeetingOutput:
        meeting = await self._repo.get_by_id(data.meeting_id)
        if meeting is None:
            raise MeetingNotFoundError(data.meeting_id)
        meeting.update(
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            location=data.location,
            status=data.status,
        )
        saved = await self._repo.save(meeting)
        return MeetingOutput.from_entity(saved)
