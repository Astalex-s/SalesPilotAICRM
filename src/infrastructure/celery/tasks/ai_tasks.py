"""
Celery задачи для AI-операций.

Каждая задача:
1. Принимает примитивы (JSON-сериализуемые аргументы).
2. Запускает async реализацию через asyncio.run().
3. Возвращает dict — сериализованный выходной DTO.
4. Повторяет попытку при сетевых ошибках (до 3 раз, интервал 60 сек).

Никакой бизнес-логики — только оркестрация зависимостей.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from celery import Task

from src.application.dtos.ai_dtos import (
    DealForecastInput,
    GenerateEmailInput,
    LeadScoreInput,
    NextBestActionInput,
)
from src.application.use_cases.forecast_deal import ForecastDealUseCase
from src.application.use_cases.generate_email import GenerateEmailUseCase
from src.application.use_cases.get_next_best_action import GetNextBestActionUseCase
from src.application.use_cases.score_lead import ScoreLeadUseCase
from src.infrastructure.ai.ai_service import OpenAIService
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.celery.task_session import get_task_session
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository

logger = logging.getLogger(__name__)


# ── Оценка лида ────────────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.ai.score_lead",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def score_lead_task(self: Task, lead_id: str) -> dict[str, Any]:
    """Celery задача: AI-оценка лида.

    Args:
        lead_id: строковое представление UUID лида.

    Returns:
        Сериализованный LeadScoreOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = ScoreLeadUseCase(
                lead_repo=SqlLeadRepository(session),
                ai_service=OpenAIService(),
            )
            result = await use_case.execute(LeadScoreInput(lead_id=UUID(lead_id)))
            return result.model_dump(mode="json")

    try:
        logger.info("score_lead_task: старт, lead_id=%s", lead_id)
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("score_lead_task: ошибка, lead_id=%s", lead_id)
        raise self.retry(exc=exc)


# ── Прогноз сделки ─────────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.ai.forecast_deal",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def forecast_deal_task(self: Task, deal_id: str) -> dict[str, Any]:
    """Celery задача: AI-прогноз вероятности закрытия сделки.

    Args:
        deal_id: строковое представление UUID сделки.

    Returns:
        Сериализованный DealForecastOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = ForecastDealUseCase(
                deal_repo=SqlDealRepository(session),
                ai_service=OpenAIService(),
            )
            result = await use_case.execute(DealForecastInput(deal_id=UUID(deal_id)))
            return result.model_dump(mode="json")

    try:
        logger.info("forecast_deal_task: старт, deal_id=%s", deal_id)
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("forecast_deal_task: ошибка, deal_id=%s", deal_id)
        raise self.retry(exc=exc)


# ── Генерация письма ───────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.ai.generate_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_email_task(
    self: Task,
    lead_id: str,
    tone: str = "friendly",
    extra_context: str | None = None,
) -> dict[str, Any]:
    """Celery задача: AI-генерация персонализированного письма для лида.

    Args:
        lead_id: строковое представление UUID лида.
        tone: тон письма — formal | friendly | assertive.
        extra_context: дополнительный контекст от менеджера (опционально).

    Returns:
        Сериализованный GenerateEmailOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = GenerateEmailUseCase(
                lead_repo=SqlLeadRepository(session),
                ai_service=OpenAIService(),
            )
            result = await use_case.execute(
                GenerateEmailInput(
                    lead_id=UUID(lead_id),
                    tone=tone,  # type: ignore[arg-type]
                    extra_context=extra_context,
                )
            )
            return result.model_dump(mode="json")

    try:
        logger.info("generate_email_task: старт, lead_id=%s, tone=%s", lead_id, tone)
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("generate_email_task: ошибка, lead_id=%s", lead_id)
        raise self.retry(exc=exc)


# ── Следующее наилучшее действие ───────────────────────────────────────────────

@celery_app.task(
    name="tasks.ai.next_best_action",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def next_best_action_task(
    self: Task,
    entity_type: str,
    entity_id: str,
) -> dict[str, Any]:
    """Celery задача: AI-рекомендация следующего действия для лида или сделки.

    Args:
        entity_type: "lead" | "deal".
        entity_id: строковое представление UUID сущности.

    Returns:
        Сериализованный NextBestActionOutput.
    """
    async def _run() -> dict[str, Any]:
        async with get_task_session() as session:
            use_case = GetNextBestActionUseCase(
                lead_repo=SqlLeadRepository(session),
                deal_repo=SqlDealRepository(session),
                ai_service=OpenAIService(),
            )
            result = await use_case.execute(
                NextBestActionInput(
                    entity_type=entity_type,  # type: ignore[arg-type]
                    entity_id=UUID(entity_id),
                )
            )
            return result.model_dump(mode="json")

    try:
        logger.info(
            "next_best_action_task: старт, %s entity_id=%s", entity_type, entity_id
        )
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception(
            "next_best_action_task: ошибка, %s entity_id=%s", entity_type, entity_id
        )
        raise self.retry(exc=exc)
