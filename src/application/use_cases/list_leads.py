"""
ListLeadsUseCase — use case получения списка лидов с опциональной фильтрацией.

Единственная ответственность: применить фильтры и вернуть список DTO.
Приоритет фильтров: owner_id > status > все лиды.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import LeadOutput, ListLeadsInput
from src.domain.repositories.lead_repository import ILeadRepository


class ListLeadsUseCase:
    """Возвращает список лидов с опциональной фильтрацией по владельцу или статусу."""

    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo

    async def execute(self, data: ListLeadsInput) -> list[LeadOutput]:
        """Выполняет поиск лидов по переданным фильтрам.

        Последовательность применения фильтров:
        1. owner_id — если задан, возвращает только лиды пользователя.
        2. status   — если задан (без owner_id), фильтрует по статусу.
        3. Без фильтров — возвращает все лиды (административный режим).
        """
        if data.owner_id is not None:
            leads = await self._lead_repo.find_by_owner(data.owner_id)
        elif data.status is not None:
            leads = await self._lead_repo.find_by_status(data.status)
        else:
            leads = await self._lead_repo.find_all()

        return [LeadOutput.from_entity(lead) for lead in leads]
