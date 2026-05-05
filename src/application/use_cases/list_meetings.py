from __future__ import annotations

from src.application.dtos.meeting_dtos import ListMeetingsInput, MeetingOutput
from src.domain.repositories.meeting_repository import IMeetingRepository


class ListMeetingsUseCase:
    def __init__(self, meeting_repo: IMeetingRepository) -> None:
        self._repo = meeting_repo

    async def execute(self, data: ListMeetingsInput) -> list[MeetingOutput]:
        meetings = await self._repo.find_all(
            lead_id=data.lead_id,
            deal_id=data.deal_id,
            from_date=data.from_date,
            to_date=data.to_date,
            status=data.status,
        )
        return [MeetingOutput.from_entity(m) for m in meetings]
