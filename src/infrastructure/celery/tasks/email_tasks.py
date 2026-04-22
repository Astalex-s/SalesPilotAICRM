"""
Celery задачи для Gmail-операций.

send_email_task  — фоновая отправка письма через Gmail.
fetch_emails_task — фоновая синхронизация писем из Gmail.

Каждая задача принимает JSON-сериализуемые аргументы,
запускает async use case через asyncio.run() и
повторяет при сетевых ошибках (до 3 раз).
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from celery import Task

from src.application.dtos.email_message_dtos import FetchEmailsInput, SendEmailInput
from src.application.use_cases.fetch_emails import FetchEmailsUseCase
from src.application.use_cases.send_email import SendEmailUseCase
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.celery.task_session import get_task_session
from src.infrastructure.config.settings import settings
from src.infrastructure.database.repositories.activity_repository import SqlActivityRepository
from src.infrastructure.database.repositories.email_message_repository import (
    SqlEmailMessageRepository,
)
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository
from src.infrastructure.gmail.gmail_service import GmailService
from src.infrastructure.gmail.token_storage import FileTokenStorage

logger = logging.getLogger(__name__)


# ── Вспомогательная фабрика Gmail сервиса ─────────────────────────────────────

def _build_gmail_service() -> GmailService:
    """Создаёт GmailService из настроек — используется внутри задач."""
    return GmailService(
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        redirect_uri=settings.GMAIL_REDIRECT_URI,
        token_storage=FileTokenStorage(settings.GMAIL_TOKEN_FILE),
    )


# ── Отправка письма ────────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.email.send",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_email_task(self: Task, payload: dict[str, Any]) -> dict[str, Any]:
    """Celery задача: отправка письма через Gmail.

    Args:
        payload: сериализованный SendEmailInput (все поля — примитивы/строки).

    Returns:
        Сериализованный EmailMessageOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = SendEmailUseCase(
                email_service=_build_gmail_service(),
                email_repo=SqlEmailMessageRepository(session),
                lead_repo=SqlLeadRepository(session),
                activity_repo=SqlActivityRepository(session),
            )
            data = SendEmailInput.model_validate(payload)
            result = await use_case.execute(data)
            return result.model_dump(mode="json")

    try:
        logger.info("send_email_task: старт, to=%s", payload.get("to"))
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("send_email_task: ошибка, to=%s", payload.get("to"))
        raise self.retry(exc=exc)


# ── Синхронизация писем ────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.email.fetch",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def fetch_emails_task(
    self: Task,
    query: str = "",
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Celery задача: синхронизация писем из Gmail в CRM.

    Args:
        query: строка поиска Gmail (например, "from:client@corp.com").
        max_results: максимальное количество писем (1–500).

    Returns:
        Список сериализованных EmailMessageOutput для новых писем.
    """
    async def _run() -> list[dict[str, Any]]:
        async with get_task_session() as session:
            use_case = FetchEmailsUseCase(
                email_service=_build_gmail_service(),
                email_repo=SqlEmailMessageRepository(session),
                lead_repo=SqlLeadRepository(session),
            )
            results = await use_case.execute(
                FetchEmailsInput(query=query, max_results=max_results)
            )
            return [r.model_dump(mode="json") for r in results]

    try:
        logger.info(
            "fetch_emails_task: старт, query=%r, max_results=%d", query, max_results
        )
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("fetch_emails_task: ошибка")
        raise self.retry(exc=exc)
