"""
Celery задачи периодической синхронизации (Celery Beat).

fetch_emails_periodic — запускается по расписанию,
ставит в очередь fetch_emails_task для фоновой синхронизации писем.
"""
from __future__ import annotations

import logging

from src.infrastructure.celery.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.sync.fetch_emails_periodic")
def fetch_emails_periodic_task(
    query: str = "",
    max_results: int = 100,
) -> dict:
    """Периодическая задача синхронизации писем из Gmail.

    Запускается Celery Beat согласно расписанию CELERY_EMAIL_SYNC_INTERVAL_SECONDS.
    Делегирует выполнение fetch_emails_task через .delay() — не дублирует логику.

    Args:
        query: строка поиска Gmail.
        max_results: максимальное количество писем за один запуск.

    Returns:
        Словарь с task_id дочерней задачи.
    """
    # Импорт здесь — избегаем циклических зависимостей при инициализации Celery
    from src.infrastructure.celery.tasks.email_tasks import fetch_emails_task

    logger.info(
        "fetch_emails_periodic_task: ставим задачу синхронизации в очередь, "
        "query=%r, max_results=%d",
        query,
        max_results,
    )
    result = fetch_emails_task.delay(query=query, max_results=max_results)
    return {"enqueued_task_id": result.id}
