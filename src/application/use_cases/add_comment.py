"""
AddCommentUseCase — добавляет комментарий (заметку) к лиду или сделке.

Комментарий сохраняется как Activity(type=NOTE) — append-only запись в журнале.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.activity_dtos import ActivityOutput
from src.domain.entities.activity import Activity, EntityType
from src.domain.repositories.activity_repository import IActivityRepository


class AddCommentUseCase:
    def __init__(self, activity_repo: IActivityRepository) -> None:
        self._activity_repo = activity_repo

    async def execute(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        performed_by_id: UUID,
        body: str,
    ) -> ActivityOutput:
        activity = Activity.log_note(
            entity_type=entity_type,
            entity_id=entity_id,
            performed_by_id=performed_by_id,
            body=body,
        )
        saved = await self._activity_repo.save(activity)
        return ActivityOutput.from_entity(saved)
