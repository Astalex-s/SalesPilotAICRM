"""
Порт AI-сервиса — Application layer.
Определяет контракт для всех AI-операций CRM.
Конкретные провайдеры (OpenAI, Anthropic и т.д.) реализуют этот интерфейс
в слое Infrastructure. Use Cases зависят ТОЛЬКО от IAIService.

Правило: AI никогда не вызывается напрямую из контроллеров или use cases —
только через этот порт.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ── Результирующие типы (пересекают границу AI-сервиса) ───────────────────────

@dataclass(frozen=True)
class LeadScore:
    """Результат оценки лида AI-моделью."""

    score: float                         # вероятность конвертации: 0.0 – 1.0
    reasoning: str                       # объяснение оценки
    recommended_actions: list[str]       # список рекомендуемых действий


@dataclass(frozen=True)
class DealForecast:
    """Прогноз вероятности закрытия сделки."""

    win_probability: float               # вероятность выигрыша: 0.0 – 1.0
    risk_factors: list[str]             # факторы риска
    opportunities: list[str]            # возможности для ускорения


@dataclass(frozen=True)
class NextBestAction:
    """Следующее наилучшее действие для сущности CRM."""

    action: str                          # конкретное действие
    priority: str                        # "high" | "medium" | "low"
    reasoning: str                       # обоснование


@dataclass(frozen=True)
class EmailDraft:
    """Черновик email-сообщения, сгенерированный AI."""

    subject: str
    body: str


# ── Интерфейс AI-сервиса ───────────────────────────────────────────────────────

class IAIService(ABC):
    """Контракт для всех AI-операций в CRM.

    Use Cases получают реализацию через dependency injection.
    Входные данные передаются как dict[str, Any] — доменные объекты
    сериализуются до пересечения границы сервиса.
    """

    @abstractmethod
    async def score_lead(self, lead_context: dict[str, Any]) -> LeadScore:
        """Оценивает лида и возвращает вероятность конвертации.

        Args:
            lead_context: сериализованные данные лида (имя, email, компания,
                          источник, статус, заметки).
        Returns:
            LeadScore с оценкой 0.0–1.0, обоснованием и рекомендациями.
        """
        ...

    @abstractmethod
    async def forecast_deal(self, deal_context: dict[str, Any]) -> DealForecast:
        """Прогнозирует вероятность закрытия сделки.

        Args:
            deal_context: сериализованные данные сделки (заголовок, сумма,
                          статус, этап, компания, ожидаемая дата закрытия).
        Returns:
            DealForecast с вероятностью, факторами риска и возможностями.
        """
        ...

    @abstractmethod
    async def next_best_action(
        self, entity_context: dict[str, Any]
    ) -> NextBestAction:
        """Определяет следующее наилучшее действие для лида или сделки.

        Args:
            entity_context: сериализованные данные сущности с полем
                            entity_type ("lead" | "deal").
        Returns:
            NextBestAction с действием, приоритетом и обоснованием.
        """
        ...

    @abstractmethod
    async def generate_email(
        self,
        lead_context: dict[str, Any],
        tone: str,
        extra_context: str | None,
    ) -> EmailDraft:
        """Генерирует персонализированное email-сообщение для лида.

        Args:
            lead_context: сериализованные данные лида.
            tone: тон письма — "formal" | "friendly" | "assertive".
            extra_context: дополнительный контекст от менеджера (опционально).
        Returns:
            EmailDraft с темой и телом письма.
        """
        ...
