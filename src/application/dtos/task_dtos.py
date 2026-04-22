"""
DTO для операций с фоновыми задачами.
Pydantic-модели — граница валидации на входе и выходе API слоя.
Нет зависимостей на ORM, Celery или FastAPI.
"""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ── Входные DTO — задачи на отправку email ─────────────────────────────────────

class EnqueueSendEmailInput(BaseModel):
    """Тело запроса для постановки задачи отправки письма в очередь."""

    to: str
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)
    lead_id: UUID | None = None
    performed_by_id: UUID
    thread_id: str | None = None


class EnqueueFetchEmailsInput(BaseModel):
    """Тело запроса для постановки задачи синхронизации писем в очередь."""

    query: str = ""
    max_results: int = Field(default=50, ge=1, le=500)


# ── Выходные DTO ───────────────────────────────────────────────────────────────

class TaskEnqueuedOutput(BaseModel):
    """Ответ на успешную постановку задачи в очередь."""

    task_id: str
    task_name: str
    status: str = "ENQUEUED"
    message: str


class TaskStatusOutput(BaseModel):
    """Текущий статус задачи в очереди."""

    task_id: str
    status: str = Field(
        description="PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED"
    )
    result: dict[str, Any] | None = None
    error: str | None = None
