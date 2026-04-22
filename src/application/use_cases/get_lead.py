"""
GetLeadUseCase — use case получения одного лида по ID.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import GetLeadInput, LeadOutput
from src.application.exceptions import LeadNotFoundError
from src.domain.repositories.lead_repository import ILeadRepository


class GetLeadUseCase:
    """Возвращает лида по первичному ключу."""

    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo

    async def execute(self, data: GetLeadInput) -> LeadOutput:
        """Загружает лида; выбрасывает LeadNotFoundError если не найден."""
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)
        return LeadOutput.from_entity(lead)
