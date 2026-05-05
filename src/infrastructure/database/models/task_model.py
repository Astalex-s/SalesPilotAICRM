"""
TaskModel — ORM-модель таблицы tasks (CRM-задачи).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.task import Task
from src.domain.value_objects.enums import TaskStatus
from src.infrastructure.database.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assignee_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    created_by_id: Mapped[UUID] = mapped_column(nullable=False)
    lead_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    deal_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="taskstatus"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_entity(self) -> Task:
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            due_date=self.due_date,
            assignee_id=self.assignee_id,
            created_by_id=self.created_by_id,
            lead_id=self.lead_id,
            deal_id=self.deal_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, task: Task) -> TaskModel:
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            assignee_id=task.assignee_id,
            created_by_id=task.created_by_id,
            lead_id=task.lead_id,
            deal_id=task.deal_id,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
