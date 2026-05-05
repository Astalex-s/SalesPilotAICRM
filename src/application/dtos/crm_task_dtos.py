"""
DTO для CRM-задач.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.entities.task import Task
from src.domain.value_objects.enums import TaskStatus


class CreateTaskInput(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assignee_id: UUID
    lead_id: UUID | None = None
    deal_id: UUID | None = None

    @field_validator("title")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название задачи не может быть пустым.")
        return v.strip()


class UpdateTaskInput(BaseModel):
    task_id: UUID
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    assignee_id: UUID | None = None
    status: TaskStatus | None = None


class ListTasksInput(BaseModel):
    assignee_id: UUID | None = None
    lead_id: UUID | None = None
    deal_id: UUID | None = None
    status: TaskStatus | None = None
    overdue_only: bool = False


class TaskOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    due_date: datetime | None
    assignee_id: UUID
    created_by_id: UUID
    lead_id: UUID | None
    deal_id: UUID | None
    status: TaskStatus
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, task: Task) -> TaskOutput:
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
            is_overdue=task.is_overdue,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
