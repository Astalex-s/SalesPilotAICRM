"""
ListDealsUseCase — use case получения списка сделок с опциональной фильтрацией.

Единственная ответственность: применить фильтры и вернуть список DTO.
Приоритет фильтров: pipeline_id > stage_id > owner_id > все сделки.
"""
from __future__ import annotations

from src.application.dtos.deal_dtos import DealOutput, ListDealsInput
from src.domain.repositories.deal_repository import IDealRepository


class ListDealsUseCase:
    """Возвращает список сделок с опциональной фильтрацией."""

    def __init__(self, deal_repo: IDealRepository) -> None:
        self._deal_repo = deal_repo

    async def execute(self, data: ListDealsInput) -> list[DealOutput]:
        """Выполняет поиск сделок по переданным фильтрам.

        Последовательность применения фильтров:
        1. pipeline_id — все сделки в воронке.
        2. stage_id    — все сделки на конкретном этапе.
        3. owner_id    — все сделки пользователя.
        4. Без фильтров — все сделки (административный режим).
        """
        if data.pipeline_id is not None:
            deals = await self._deal_repo.find_by_pipeline(data.pipeline_id)
        elif data.stage_id is not None:
            deals = await self._deal_repo.find_by_stage(data.stage_id)
        elif data.owner_id is not None:
            deals = await self._deal_repo.find_by_owner(data.owner_id)
        else:
            deals = await self._deal_repo.find_all()

        return [DealOutput.from_entity(deal) for deal in deals]
