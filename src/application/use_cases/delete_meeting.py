from __future__ import annotations

from uuid import UUID

from src.application.exceptions import MeetingNotFoundError
from src.domain.repositories.meeting_repository import IMeetingRepository


class DeleteMeetingUseCase:
    def __init__(self, meeting_repo: IMeetingRepository) -> None:
        self._repo = meeting_repo

    async def execute(self, meeting_id: UUID) -> None:
        meeting = await self._repo.get_by_id(meeting_id)
        if meeting is None:
            raise MeetingNotFoundError(meeting_id)
        await self._repo.delete(meeting_id)
