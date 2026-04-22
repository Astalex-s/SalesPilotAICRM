"""
ListLeadActivitiesUseCase — use case получения журнала активностей лида.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.activity_dtos import ActivityOutput
from src.domain.entities.activity import EntityType
from src.domain.repositories.activity_repository import IActivityRepository


class ListLeadActivitiesUseCase:
    """Возвращает список активностей для конкретного лида, начиная с последней."""

    def __init__(self, activity_repo: IActivityRepository) -> None:
        self._activity_repo = activity_repo

    async def execute(self, lead_id: UUID) -> list[ActivityOutput]:
        """Загружает все активности лида и возвращает их как DTO."""
        entity_type: EntityType = "lead"
        activities = await self._activity_repo.find_by_entity(entity_type, lead_id)
        return [ActivityOutput.from_entity(a) for a in activities]
