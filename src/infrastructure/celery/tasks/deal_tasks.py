"""
Celery задачи для операций со сделками.

notify_overdue_deals_task — периодически уведомляет о просроченных сделках через Telegram.
Запускается Celery Beat раз в сутки.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.notify_overdue_deals import NotifyOverdueDealsUseCase
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.celery.task_session import get_task_session
from src.infrastructure.config.settings import settings
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.telegram.telegram_service import TelegramService

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.deals.notify_overdue",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def notify_overdue_deals_task(self: Any) -> dict[str, Any]:
    """Celery задача: отправка Telegram-уведомлений о просроченных сделках.

    Запускается Celery Beat раз в сутки (CELERY_OVERDUE_DEALS_CHECK_INTERVAL).

    Returns:
        {"overdue_count": N} — количество найденных просроченных сделок.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            telegram_service = TelegramService(
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                notification_chat_id=settings.TELEGRAM_NOTIFICATION_CHAT_ID,
            )
            use_case = NotifyOverdueDealsUseCase(
                telegram_service=telegram_service,
                deal_repo=SqlDealRepository(session),
            )
            count = await use_case.execute()
            return {"overdue_count": count}

    try:
        logger.info("notify_overdue_deals_task: старт")
        return asyncio.run(_run())
    except TelegramNotConfiguredError:
        logger.warning("notify_overdue_deals_task: Telegram не настроен, пропускаем")
        return {"overdue_count": 0}
    except Exception as exc:
        logger.exception("notify_overdue_deals_task: ошибка")
        raise self.retry(exc=exc)
