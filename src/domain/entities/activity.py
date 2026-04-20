"""
Доменная сущность Activity — неизменяемая запись журнала аудита.
Фиксирует каждое значимое действие над лидом или сделкой.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from src.domain.value_objects.enums import ActivityType

# Допустимые типы сущностей, к которым могут быть привязаны активности
EntityType = Literal["lead", "deal"]


@dataclass(frozen=True)
class Activity:
    """Неизменяемая запись о действии в CRM.

    Активности формируют append-only журнал аудита.
    После создания изменение невозможно.

    Инварианты:
    - body не может быть пустым
    - entity_id и performed_by_id обязательны
    - occurred_at устанавливается при создании и не меняется
    """

    id: UUID
    entity_type: EntityType
    entity_id: UUID
    activity_type: ActivityType
    performed_by_id: UUID
    body: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        if not self.body.strip():
            raise ValueError("Тело активности не может быть пустым.")

    # ── Фабрики ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        entity_type: EntityType,
        entity_id: UUID,
        activity_type: ActivityType,
        performed_by_id: UUID,
        body: str,
    ) -> Activity:
        """Создаёт новую активность с временной меткой на текущий момент."""
        return cls(
            id=uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            activity_type=activity_type,
            performed_by_id=performed_by_id,
            body=body,
            occurred_at=datetime.now(timezone.utc),
        )

    @classmethod
    def log_note(
        cls,
        entity_type: EntityType,
        entity_id: UUID,
        performed_by_id: UUID,
        body: str,
    ) -> Activity:
        """Фабрика для произвольной заметки."""
        return cls.create(
            entity_type=entity_type,
            entity_id=entity_id,
            activity_type=ActivityType.NOTE,
            performed_by_id=performed_by_id,
            body=body,
        )

    @classmethod
    def log_status_change(
        cls,
        entity_type: EntityType,
        entity_id: UUID,
        performed_by_id: UUID,
        from_status: str,
        to_status: str,
    ) -> Activity:
        """Фабрика для записи об изменении статуса."""
        return cls.create(
            entity_type=entity_type,
            entity_id=entity_id,
            activity_type=ActivityType.STATUS_CHANGE,
            performed_by_id=performed_by_id,
            body=f"Статус изменён: '{from_status}' → '{to_status}'.",
        )

    @classmethod
    def log_stage_change(
        cls,
        deal_id: UUID,
        performed_by_id: UUID,
        from_stage: str,
        to_stage: str,
    ) -> Activity:
        """Фабрика для записи о смене этапа сделки."""
        return cls.create(
            entity_type="deal",
            entity_id=deal_id,
            activity_type=ActivityType.STAGE_CHANGE,
            performed_by_id=performed_by_id,
            body=f"Сделка перемещена из этапа '{from_stage}' → '{to_stage}'.",
        )

    @classmethod
    def log_lead_conversion(
        cls,
        lead_id: UUID,
        deal_id: UUID,
        performed_by_id: UUID,
        lead_name: str,
        deal_title: str,
    ) -> Activity:
        """Фабрика для записи о конвертации лида в сделку."""
        return cls.create(
            entity_type="lead",
            entity_id=lead_id,
            activity_type=ActivityType.LEAD_CONVERTED,
            performed_by_id=performed_by_id,
            body=(
                f"Лид '{lead_name}' конвертирован в сделку '{deal_title}' "
                f"(ID сделки: {deal_id})."
            ),
        )

    def __repr__(self) -> str:
        return (
            f"Activity(id={self.id}, type={self.activity_type.value}, "
            f"entity={self.entity_type}:{self.entity_id})"
        )
