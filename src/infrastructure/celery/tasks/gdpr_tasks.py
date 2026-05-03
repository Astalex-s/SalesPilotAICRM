"""
Celery задачи для GDPR-операций.

apply_retention_policy_task — периодически удаляет данные старше retention_days.
Запускается Celery Beat раз в сутки.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.application.use_cases.apply_retention_policy import ApplyRetentionPolicyUseCase
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.celery.task_session import get_task_session
from src.infrastructure.config.settings import settings
from src.infrastructure.database.repositories.activity_repository import SqlActivityRepository
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.database.repositories.email_message_repository import SqlEmailMessageRepository
from src.infrastructure.database.repositories.gdpr_audit_repository import SqlGdprAuditRepository
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.gdpr.apply_retention_policy",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def apply_retention_policy_task(self: Any) -> dict[str, Any]:
    """Celery задача: применение GDPR retention policy.

    Удаляет лиды и сделки старше GDPR_RETENTION_DAYS дней.
    Запускается Celery Beat раз в сутки (CELERY_RETENTION_CHECK_INTERVAL).

    Returns:
        Сериализованный RetentionPolicyOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = ApplyRetentionPolicyUseCase(
                lead_repo=SqlLeadRepository(session),
                deal_repo=SqlDealRepository(session),
                email_repo=SqlEmailMessageRepository(session),
                activity_repo=SqlActivityRepository(session),
                gdpr_audit_repo=SqlGdprAuditRepository(session),
            )
            result = await use_case.execute(retention_days=settings.GDPR_RETENTION_DAYS)
            return result.model_dump(mode="json")

    try:
        logger.info(
            "apply_retention_policy_task: старт, retention_days=%d",
            settings.GDPR_RETENTION_DAYS,
        )
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("apply_retention_policy_task: ошибка")
        raise self.retry(exc=exc)
