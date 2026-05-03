"""
DTO для Telegram-уведомлений.
Pydantic-модели — граница валидации на входе и выходе use case.
Нет зависимостей на ORM или FastAPI.
"""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, HttpUrl

from src.domain.value_objects.enums import LeadSource


# ── Входные DTO — use cases ────────────────────────────────────────────────────

class NotifyNewLeadInput(BaseModel):
    """Входные данные для уведомления о новом лиде."""

    lead_id: UUID
    first_name: str
    last_name: str
    email: str
    company: str | None = None
    source: LeadSource


class NotifyDealStageChangeInput(BaseModel):
    """Входные данные для уведомления о смене этапа сделки."""

    deal_id: UUID
    deal_title: str
    new_stage_id: UUID
    pipeline_id: UUID


class NotifyNewDealInput(BaseModel):
    """Входные данные для уведомления о создании новой сделки."""

    deal_id: UUID
    deal_title: str
    lead_name: str
    value_amount: float
    value_currency: str


# ── Входные DTO — API ──────────────────────────────────────────────────────────

class TelegramWebhookSetInput(BaseModel):
    """Тело запроса на установку вебхука."""

    url: HttpUrl
    secret_token: str | None = None


# ── Выходные DTO — API ─────────────────────────────────────────────────────────

class TelegramStatusOutput(BaseModel):
    """Статус Telegram-интеграции."""

    configured: bool
    webhook_url: str
    webhook_pending_updates: int


class TelegramWebhookSetOutput(BaseModel):
    """Результат установки вебхука."""

    success: bool
    message: str
