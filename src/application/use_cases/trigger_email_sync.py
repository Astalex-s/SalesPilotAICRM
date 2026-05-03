"""
TriggerEmailSyncUseCase — ставит задачу синхронизации писем в очередь Celery.
Возвращает task_id немедленно, не дожидаясь результата.
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import EmailSyncOutput
from src.application.ports.task_service import ITaskService


class TriggerEmailSyncUseCase:
    """Инициирует фоновую синхронизацию Gmail через Celery."""

    def __init__(self, task_service: ITaskService) -> None:
        self._task_service = task_service

    async def execute(self, query: str = "", max_results: int = 100) -> EmailSyncOutput:
        """Ставит fetch_emails_task в очередь и возвращает task_id."""
        enqueued = self._task_service.enqueue_fetch_emails(
            query=query,
            max_results=max_results,
        )
        return EmailSyncOutput(task_id=enqueued.task_id)
