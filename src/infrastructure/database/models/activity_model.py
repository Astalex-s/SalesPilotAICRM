"""
ActivityModel — ORM-модель таблицы activities.
Append-only журнал аудита: строки только добавляются, никогда не обновляются.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.activity import Activity, EntityType
from src.domain.value_objects.enums import ActivityType
from src.infrastructure.database.base import Base


class ActivityModel(Base):
    """ORM-модель для таблицы activities."""

    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    # entity_type — строковый дискриминатор ("lead" | "deal")
    entity_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    entity_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    activity_type: Mapped[ActivityType] = mapped_column(
        SAEnum(ActivityType, name="activitytype", values_callable=lambda e: [x.value for x in e]),
        nullable=False
    )
    performed_by_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> Activity:
        """Преобразует ORM-строку в доменную сущность Activity."""
        return Activity(
            id=self.id,
            entity_type=self.entity_type,  # type: ignore[arg-type]
            entity_id=self.entity_id,
            activity_type=self.activity_type,
            performed_by_id=self.performed_by_id,
            body=self.body,
            occurred_at=self.occurred_at,
        )

    @classmethod
    def from_entity(cls, activity: Activity) -> ActivityModel:
        """Преобразует доменную сущность Activity в ORM-модель."""
        return cls(
            id=activity.id,
            entity_type=activity.entity_type,
            entity_id=activity.entity_id,
            activity_type=activity.activity_type,
            performed_by_id=activity.performed_by_id,
            body=activity.body,
            occurred_at=activity.occurred_at,
        )
