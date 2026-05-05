"""
ListDealActivitiesUseCase — возвращает журнал активностей сделки.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.activity_dtos import ActivityOutput
from src.domain.entities.activity import EntityType
from src.domain.repositories.activity_repository import IActivityRepository


class ListDealActivitiesUseCase:
    def __init__(self, activity_repo: IActivityRepository) -> None:
        self._activity_repo = activity_repo

    async def execute(self, deal_id: UUID) -> list[ActivityOutput]:
        entity_type: EntityType = "deal"
        activities = await self._activity_repo.find_by_entity(entity_type, deal_id)
        return [ActivityOutput.from_entity(a) for a in activities]
