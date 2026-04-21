"""
OpenAIService — реализация IAIService через OpenAI SDK.
Ответственность: HTTP-взаимодействие с OpenAI, retry-логика, логирование.
Никакой бизнес-логики — только I/O.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryError,
)

from src.application.ports.ai_service import (
    DealForecast,
    EmailDraft,
    IAIService,
    LeadScore,
    NextBestAction,
)
from src.infrastructure.ai.prompts import (
    FORECAST_DEAL_SYSTEM,
    GENERATE_EMAIL_SYSTEM,
    NEXT_BEST_ACTION_LEAD_SYSTEM,
    SCORE_LEAD_SYSTEM,
    forecast_deal_user,
    generate_email_user,
    next_best_action_user,
    score_lead_user,
)
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

# Типы исключений OpenAI, при которых выполняется повтор запроса
_RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, APITimeoutError)


class OpenAIService(IAIService):
    """Адаптер AI на базе OpenAI SDK.

    Все запросы к API:
    - выполняются асинхронно через AsyncOpenAI
    - защищены retry-логикой (exponential backoff)
    - логируют вход/выход на уровне DEBUG и ошибки на WARNING/ERROR
    - возвращают строго типизированные result dataclasses
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=0,           # retry управляется через tenacity
        )
        self._model = settings.OPENAI_MODEL

    # ── Публичный API ─────────────────────────────────────────────────────────

    async def score_lead(self, lead_context: dict[str, Any]) -> LeadScore:
        """Оценивает лида: вероятность конвертации + рекомендации."""
        logger.debug("score_lead: запрос для лида '%s'", lead_context.get("name"))

        raw = await self._chat_json(
            system=SCORE_LEAD_SYSTEM,
            user=score_lead_user(lead_context),
        )

        logger.debug("score_lead: ответ получен, score=%.2f", raw.get("score", 0))

        return LeadScore(
            score=float(raw["score"]),
            reasoning=raw["reasoning"],
            recommended_actions=raw.get("recommended_actions", []),
        )

    async def forecast_deal(self, deal_context: dict[str, Any]) -> DealForecast:
        """Прогнозирует вероятность закрытия сделки."""
        logger.debug("forecast_deal: запрос для сделки '%s'", deal_context.get("title"))

        raw = await self._chat_json(
            system=FORECAST_DEAL_SYSTEM,
            user=forecast_deal_user(deal_context),
        )

        logger.debug(
            "forecast_deal: ответ получен, win_probability=%.2f",
            raw.get("win_probability", 0),
        )

        return DealForecast(
            win_probability=float(raw["win_probability"]),
            risk_factors=raw.get("risk_factors", []),
            opportunities=raw.get("opportunities", []),
        )

    async def next_best_action(
        self, entity_context: dict[str, Any]
    ) -> NextBestAction:
        """Определяет следующее наилучшее действие для лида или сделки."""
        entity_type = entity_context.get("entity_type", "lead")
        logger.debug("next_best_action: запрос для %s", entity_type)

        raw = await self._chat_json(
            system=NEXT_BEST_ACTION_LEAD_SYSTEM,
            user=next_best_action_user(entity_context),
        )

        logger.debug("next_best_action: действие='%s'", raw.get("action"))

        return NextBestAction(
            action=raw["action"],
            priority=raw.get("priority", "medium"),
            reasoning=raw["reasoning"],
        )

    async def generate_email(
        self,
        lead_context: dict[str, Any],
        tone: str,
        extra_context: str | None,
    ) -> EmailDraft:
        """Генерирует персонализированное email-письмо."""
        logger.debug(
            "generate_email: запрос для '%s', tone=%s",
            lead_context.get("name"),
            tone,
        )

        raw = await self._chat_json(
            system=GENERATE_EMAIL_SYSTEM,
            user=generate_email_user(lead_context, tone, extra_context),
        )

        logger.debug("generate_email: тема='%s'", raw.get("subject"))

        return EmailDraft(
            subject=raw["subject"],
            body=raw["body"],
        )

    # ── Внутренние методы ─────────────────────────────────────────────────────

    async def _chat_json(self, system: str, user: str) -> dict[str, Any]:
        """Отправляет chat-запрос в OpenAI и возвращает распарсенный JSON.

        Применяет retry с экспоненциальной задержкой при временных ошибках.
        """
        try:
            return await self._chat_with_retry(system=system, user=user)
        except RetryError as exc:
            logger.error("OpenAI: все попытки исчерпаны: %s", exc)
            raise
        except Exception as exc:
            logger.error("OpenAI: неожиданная ошибка: %s", exc)
            raise

    @retry(
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _chat_with_retry(self, system: str, user: str) -> dict[str, Any]:
        """Выполняет один запрос к OpenAI Chat Completions API с retry."""
        response = await self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,         # низкая температура для детерминированных ответов
        )

        content = response.choices[0].message.content or "{}"
        logger.debug(
            "OpenAI ответ: model=%s, tokens=%d",
            response.model,
            response.usage.total_tokens if response.usage else 0,
        )

        return json.loads(content)
