"""
UpdateLeadUseCase — обновляет статус и/или заметки лида.

Переходы статусов делегированы доменной сущности Lead (машина состояний).
InvalidLeadTransitionError и LeadAlreadyConvertedError — доменные исключения,
глобально обрабатываемые как 422 Unprocessable Entity.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import UpdateLeadInput, LeadOutput
from src.application.exceptions import LeadNotFoundError
from src.domain.value_objects.enums import LeadStatus
from src.domain.repositories.lead_repository import ILeadRepository


class UpdateLeadUseCase:
    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo

    async def execute(self, data: UpdateLeadInput) -> LeadOutput:
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)

        if data.status is not None:
            match data.status:
                case LeadStatus.CONTACTED:
                    lead.contact()
                case LeadStatus.QUALIFIED:
                    lead.qualify()
                case LeadStatus.UNQUALIFIED:
                    lead.disqualify()
                case _:
                    pass  # NEW и CONVERTED нельзя установить напрямую — домен запретит

        if data.notes is not None:
            lead.add_note(data.notes)

        saved = await self._lead_repo.save(lead)
        return LeadOutput.from_entity(saved)
