"""
Доменная сущность Task — CRM-задача (to-do), привязанная к лиду или сделке.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.enums import TaskStatus


@dataclass
class Task:
    """CRM-задача: follow-up, звонок, встреча и т.п.

    Инварианты:
    - title не может быть пустым
    - lead_id или deal_id — хотя бы один задан (или оба)
    - due_date опционален
    """

    id: UUID
    title: str
    description: str | None
    due_date: datetime | None
    assignee_id: UUID
    created_by_id: UUID
    lead_id: UUID | None
    deal_id: UUID | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Название задачи не может быть пустым.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        title: str,
        created_by_id: UUID,
        assignee_id: UUID,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            title=title.strip(),
            description=description,
            due_date=due_date,
            assignee_id=assignee_id,
            created_by_id=created_by_id,
            lead_id=lead_id,
            deal_id=deal_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    # ── Команды ────────────────────────────────────────────────────────────────

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        assignee_id: UUID | None = None,
        status: TaskStatus | None = None,
    ) -> None:
        if title is not None:
            if not title.strip():
                raise ValueError("Название задачи не может быть пустым.")
            self.title = title.strip()
        if description is not None:
            self.description = description
        if due_date is not None:
            self.due_date = due_date
        if assignee_id is not None:
            self.assignee_id = assignee_id
        if status is not None:
            self.status = status
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_overdue(self) -> bool:
        if self.due_date is None or self.status in (TaskStatus.DONE, TaskStatus.CANCELLED):
            return False
        return datetime.now(timezone.utc) > self.due_date
