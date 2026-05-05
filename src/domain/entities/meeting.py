"""
Доменная сущность Meeting — встреча/событие в CRM-календаре.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.enums import MeetingStatus


@dataclass
class Meeting:
    """Встреча: звонок, визит, онлайн-конференция и т.п."""

    id: UUID
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    location: str | None
    lead_id: UUID | None
    deal_id: UUID | None
    created_by_id: UUID
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Название встречи не может быть пустым.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        title: str,
        start_time: datetime,
        created_by_id: UUID,
        description: str | None = None,
        end_time: datetime | None = None,
        location: str | None = None,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
    ) -> Meeting:
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            title=title.strip(),
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            lead_id=lead_id,
            deal_id=deal_id,
            created_by_id=created_by_id,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
            updated_at=now,
        )

    # ── Команды ────────────────────────────────────────────────────────────────

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        location: str | None = None,
        status: MeetingStatus | None = None,
    ) -> None:
        if title is not None:
            if not title.strip():
                raise ValueError("Название встречи не может быть пустым.")
            self.title = title.strip()
        if description is not None:
            self.description = description
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if location is not None:
            self.location = location
        if status is not None:
            self.status = status
        self.updated_at = datetime.now(timezone.utc)
