"""
DTO для активностей (журнал аудита).
Используется как выходная модель при запросе истории действий.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.entities.activity import Activity, EntityType
from src.domain.value_objects.enums import ActivityType


class ActivityOutput(BaseModel):
    """Данные записи из журнала аудита."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: EntityType
    entity_id: UUID
    activity_type: ActivityType
    performed_by_id: UUID
    body: str
    occurred_at: datetime

    @classmethod
    def from_entity(cls, activity: Activity) -> ActivityOutput:
        """Маппер: доменная сущность Activity → ActivityOutput DTO."""
        return cls(
            id=activity.id,
            entity_type=activity.entity_type,
            entity_id=activity.entity_id,
            activity_type=activity.activity_type,
            performed_by_id=activity.performed_by_id,
            body=activity.body,
            occurred_at=activity.occurred_at,
        )
