"""
CeleryTaskService — реализация ITaskService через Celery.

Находится в слое Infrastructure: инкапсулирует API Celery.
Никакой бизнес-логики — только постановка задач в очередь и чтение статусов.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from src.application.ports.task_service import EnqueuedTask, ITaskService, TaskStatus
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.celery.tasks.ai_tasks import (
    forecast_deal_task,
    generate_email_task,
    next_best_action_task,
    score_lead_task,
)
from src.infrastructure.celery.tasks.email_tasks import fetch_emails_task, send_email_task

logger = logging.getLogger(__name__)


class CeleryTaskService(ITaskService):
    """Реализация порта ITaskService через Celery брокер.

    Использует .delay() для постановки задач в очередь Redis.
    Результаты и статусы читаются через celery_app.AsyncResult.
    """

    # ── AI задачи ──────────────────────────────────────────────────────────────

    def enqueue_score_lead(self, lead_id: UUID) -> EnqueuedTask:
        """Ставит в очередь AI-оценку лида."""
        result = score_lead_task.delay(str(lead_id))
        logger.info("enqueue_score_lead: task_id=%s, lead_id=%s", result.id, lead_id)
        return EnqueuedTask(task_id=result.id, task_name="tasks.ai.score_lead")

    def enqueue_forecast_deal(self, deal_id: UUID) -> EnqueuedTask:
        """Ставит в очередь AI-прогноз сделки."""
        result = forecast_deal_task.delay(str(deal_id))
        logger.info("enqueue_forecast_deal: task_id=%s, deal_id=%s", result.id, deal_id)
        return EnqueuedTask(task_id=result.id, task_name="tasks.ai.forecast_deal")

    def enqueue_generate_email(
        self,
        lead_id: UUID,
        tone: str,
        extra_context: str | None,
    ) -> EnqueuedTask:
        """Ставит в очередь AI-генерацию письма."""
        result = generate_email_task.delay(
            lead_id=str(lead_id),
            tone=tone,
            extra_context=extra_context,
        )
        logger.info(
            "enqueue_generate_email: task_id=%s, lead_id=%s", result.id, lead_id
        )
        return EnqueuedTask(task_id=result.id, task_name="tasks.ai.generate_email")

    def enqueue_next_best_action(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> EnqueuedTask:
        """Ставит в очередь AI-рекомендацию следующего действия."""
        result = next_best_action_task.delay(
            entity_type=entity_type,
            entity_id=str(entity_id),
        )
        logger.info(
            "enqueue_next_best_action: task_id=%s, %s=%s",
            result.id,
            entity_type,
            entity_id,
        )
        return EnqueuedTask(task_id=result.id, task_name="tasks.ai.next_best_action")

    # ── Email задачи ───────────────────────────────────────────────────────────

    def enqueue_send_email(self, payload: dict[str, Any]) -> EnqueuedTask:
        """Ставит в очередь отправку письма через Gmail."""
        result = send_email_task.delay(payload=payload)
        logger.info(
            "enqueue_send_email: task_id=%s, to=%s", result.id, payload.get("to")
        )
        return EnqueuedTask(task_id=result.id, task_name="tasks.email.send")

    def enqueue_fetch_emails(self, query: str, max_results: int) -> EnqueuedTask:
        """Ставит в очередь синхронизацию писем из Gmail."""
        result = fetch_emails_task.delay(query=query, max_results=max_results)
        logger.info("enqueue_fetch_emails: task_id=%s", result.id)
        return EnqueuedTask(task_id=result.id, task_name="tasks.email.fetch")

    # ── Статус задачи ──────────────────────────────────────────────────────────

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Возвращает текущий статус задачи по её ID.

        Состояния Celery:
        - PENDING  — задача ещё не начата (или ID не существует)
        - STARTED  — задача выполняется (требует task_track_started=True)
        - SUCCESS  — задача успешно завершена, result содержит результат
        - FAILURE  — задача завершилась с ошибкой, result содержит исключение
        - RETRY    — задача перезапускается после ошибки
        - REVOKED  — задача была отозвана
        """
        async_result = celery_app.AsyncResult(task_id)

        task_result: dict | None = None
        error: str | None = None

        if async_result.successful():
            raw = async_result.result
            task_result = raw if isinstance(raw, dict) else {"value": raw}
        elif async_result.failed():
            error = str(async_result.result)

        return TaskStatus(
            task_id=task_id,
            status=async_result.status,
            result=task_result,
            error=error,
        )
