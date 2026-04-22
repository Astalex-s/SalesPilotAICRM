"""
ITaskService — порт приложения для постановки задач в фоновую очередь.
Абстракция изолирует бизнес-слой от Celery и любого другого брокера задач.
Реализация (CeleryTaskService) находится в Infrastructure — не здесь.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from uuid import UUID


# ── Структуры результата ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EnqueuedTask:
    """Результат постановки задачи в очередь."""

    task_id: str
    task_name: str


@dataclass(frozen=True)
class TaskStatus:
    """Текущий статус задачи в очереди."""

    task_id: str
    status: str          # PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED
    result: dict | None  # только при SUCCESS
    error: str | None    # только при FAILURE


# ── Абстрактный порт ───────────────────────────────────────────────────────────

class ITaskService(ABC):
    """Порт для постановки задач в фоновую очередь и получения их статуса.

    Контракт:
    - enqueue_* — поставить конкретную задачу в очередь, вернуть EnqueuedTask
    - get_task_status — получить текущий статус задачи по ID
    """

    # ── AI задачи ──────────────────────────────────────────────────────────────

    @abstractmethod
    def enqueue_score_lead(self, lead_id: UUID) -> EnqueuedTask:
        """Ставит в очередь задачу AI-оценки лида.

        Args:
            lead_id: идентификатор лида для оценки.
        """
        ...

    @abstractmethod
    def enqueue_forecast_deal(self, deal_id: UUID) -> EnqueuedTask:
        """Ставит в очередь задачу AI-прогноза сделки.

        Args:
            deal_id: идентификатор сделки для прогноза.
        """
        ...

    @abstractmethod
    def enqueue_generate_email(
        self,
        lead_id: UUID,
        tone: str,
        extra_context: str | None,
    ) -> EnqueuedTask:
        """Ставит в очередь задачу AI-генерации письма для лида.

        Args:
            lead_id: идентификатор лида.
            tone: тон письма — formal | friendly | assertive.
            extra_context: дополнительный контекст от менеджера.
        """
        ...

    @abstractmethod
    def enqueue_next_best_action(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> EnqueuedTask:
        """Ставит в очередь задачу AI-рекомендации следующего действия.

        Args:
            entity_type: тип сущности — "lead" | "deal".
            entity_id: идентификатор сущности.
        """
        ...

    # ── Email задачи ───────────────────────────────────────────────────────────

    @abstractmethod
    def enqueue_send_email(self, payload: dict[str, Any]) -> EnqueuedTask:
        """Ставит в очередь задачу отправки письма через Gmail.

        Args:
            payload: сериализованный SendEmailInput (все поля — примитивы).
        """
        ...

    @abstractmethod
    def enqueue_fetch_emails(self, query: str, max_results: int) -> EnqueuedTask:
        """Ставит в очередь задачу синхронизации писем из Gmail.

        Args:
            query: строка поиска Gmail.
            max_results: максимальное количество писем.
        """
        ...

    # ── Статус задачи ──────────────────────────────────────────────────────────

    @abstractmethod
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Возвращает текущий статус задачи по её ID.

        Args:
            task_id: идентификатор задачи, полученный при постановке в очередь.
        """
        ...
