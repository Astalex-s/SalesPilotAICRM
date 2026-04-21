"""
DTO для AI-операций.
Граница валидации на входе и выходе AI use cases.
Нет зависимостей на ORM, FastAPI или конкретные AI-провайдеры.
"""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ── Оценка лида ────────────────────────────────────────────────────────────────

class LeadScoreInput(BaseModel):
    """Входные данные для оценки лида."""

    lead_id: UUID


class LeadScoreOutput(BaseModel):
    """Результат оценки лида AI-моделью."""

    lead_id: UUID
    score: float = Field(ge=0.0, le=1.0, description="Вероятность конвертации 0.0–1.0")
    reasoning: str
    recommended_actions: list[str]


# ── Прогноз сделки ─────────────────────────────────────────────────────────────

class DealForecastInput(BaseModel):
    """Входные данные для прогнозирования сделки."""

    deal_id: UUID


class DealForecastOutput(BaseModel):
    """Прогноз вероятности закрытия сделки."""

    deal_id: UUID
    win_probability: float = Field(ge=0.0, le=1.0, description="Вероятность выигрыша 0.0–1.0")
    risk_factors: list[str]
    opportunities: list[str]


# ── Следующее наилучшее действие ───────────────────────────────────────────────

class NextBestActionInput(BaseModel):
    """Входные данные для получения следующего действия."""

    entity_type: Literal["lead", "deal"]
    entity_id: UUID


class NextBestActionOutput(BaseModel):
    """Рекомендованное следующее действие."""

    entity_id: UUID
    entity_type: Literal["lead", "deal"]
    action: str
    priority: Literal["high", "medium", "low"]
    reasoning: str


# ── Генерация email ────────────────────────────────────────────────────────────

class GenerateEmailInput(BaseModel):
    """Входные данные для генерации email-письма."""

    lead_id: UUID
    tone: Literal["formal", "friendly", "assertive"] = "friendly"
    extra_context: str | None = Field(
        default=None,
        description="Дополнительный контекст от менеджера (особые условия, детали встречи и т.д.)",
    )


class GenerateEmailOutput(BaseModel):
    """Сгенерированное AI email-письмо."""

    lead_id: UUID
    subject: str
    body: str
    tone: Literal["formal", "friendly", "assertive"]
