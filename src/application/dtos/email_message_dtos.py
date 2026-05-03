"""
DTO для операций с EmailMessage.
Граница валидации на входе и выходе use cases.
Нет зависимостей на ORM, FastAPI или конкретных провайдеров.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.value_objects.enums import EmailDirection


# ── Отправка письма ────────────────────────────────────────────────────────────

class SendEmailInput(BaseModel):
    """Входные данные для отправки email через Gmail."""

    to: EmailStr
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)
    lead_id: UUID | None = Field(
        default=None,
        description="Привязать письмо к указанному лиду.",
    )
    performed_by_id: UUID = Field(
        description="ID пользователя, выполняющего отправку."
    )
    thread_id: str | None = Field(
        default=None,
        description="Gmail thread ID для ответа в существующем диалоге.",
    )


# ── Загрузка писем ─────────────────────────────────────────────────────────────

class FetchEmailsInput(BaseModel):
    """Параметры загрузки писем из Gmail."""

    query: str = Field(
        default="",
        description="Строка поиска Gmail (например, 'from:client@example.com').",
    )
    max_results: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Максимальное количество загружаемых писем.",
    )


# ── Привязка к лиду ────────────────────────────────────────────────────────────

class LinkEmailToLeadInput(BaseModel):
    """Входные данные для привязки письма к лиду."""

    email_message_id: UUID
    lead_id: UUID


# ── Общий выходной DTO ─────────────────────────────────────────────────────────

class EmailMessageOutput(BaseModel):
    """Выходное представление сохранённого письма."""

    id: UUID
    gmail_message_id: str
    gmail_thread_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    body: str
    direction: EmailDirection
    received_at: datetime
    lead_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Список сохранённых писем ───────────────────────────────────────────────────

class ListStoredEmailsInput(BaseModel):
    """Параметры для листинга писем из локальной БД (без Gmail API)."""

    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# ── Фоновая синхронизация ──────────────────────────────────────────────────────

class EmailSyncOutput(BaseModel):
    """Результат постановки задачи синхронизации в очередь Celery."""

    task_id: str
    message: str = "Синхронизация почты поставлена в очередь."


# ── Треды (цепочки писем) ──────────────────────────────────────────────────────

class EmailThreadSummary(BaseModel):
    """Краткая информация о треде (для листинга)."""

    thread_id: str                  # gmail_thread_id
    subject: str
    message_count: int
    last_message_at: datetime
    participants: list[str]         # уникальные адреса из from + to
    lead_id: UUID | None


class EmailThreadDetail(BaseModel):
    """Полный тред — все письма в хронологическом порядке."""

    thread_id: str
    subject: str
    messages: list[EmailMessageOutput]


# ── OAuth2 ─────────────────────────────────────────────────────────────────────

class GmailAuthUrlOutput(BaseModel):
    """URL для инициации OAuth2-авторизации."""

    auth_url: str
    message: str = "Перейдите по ссылке для авторизации Gmail."


class GmailAuthStatusOutput(BaseModel):
    """Статус Gmail-авторизации."""

    authorized: bool
    message: str
