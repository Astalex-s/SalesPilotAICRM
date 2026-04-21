"""
Роутер /api/v1/ai — AI-эндпоинты CRM.
Тонкие контроллеры: принять запрос → use case → DTO.
AI-провайдер никогда не вызывается напрямую отсюда.
"""
from __future__ import annotations

from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.ai_dtos import (
    DealForecastInput,
    DealForecastOutput,
    GenerateEmailInput,
    GenerateEmailOutput,
    LeadScoreInput,
    LeadScoreOutput,
    NextBestActionInput,
    NextBestActionOutput,
)
from src.application.use_cases.forecast_deal import ForecastDealUseCase
from src.application.use_cases.generate_email import GenerateEmailUseCase
from src.application.use_cases.get_next_best_action import GetNextBestActionUseCase
from src.application.use_cases.score_lead import ScoreLeadUseCase
from src.interfaces.api.dependencies import (
    get_forecast_deal_use_case,
    get_generate_email_use_case,
    get_next_best_action_use_case,
    get_score_lead_use_case,
)

router = APIRouter(prefix="/ai", tags=["AI-аналитика"])


@router.post(
    "/leads/{lead_id}/score",
    response_model=LeadScoreOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Оценить лида с помощью AI",
    description=(
        "Анализирует данные лида и возвращает вероятность конвертации (0.0–1.0), "
        "обоснование оценки и список рекомендованных действий."
    ),
)
async def score_lead(
    lead_id: UUID,
    use_case: ScoreLeadUseCase = Depends(get_score_lead_use_case),
) -> LeadScoreOutput:
    """POST /api/v1/ai/leads/{lead_id}/score — AI-оценка лида."""
    return await use_case.execute(LeadScoreInput(lead_id=lead_id))


@router.post(
    "/deals/{deal_id}/forecast",
    response_model=DealForecastOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Прогноз закрытия сделки",
    description=(
        "Анализирует текущее состояние сделки и возвращает вероятность выигрыша, "
        "факторы риска и возможности для ускорения."
    ),
)
async def forecast_deal(
    deal_id: UUID,
    use_case: ForecastDealUseCase = Depends(get_forecast_deal_use_case),
) -> DealForecastOutput:
    """POST /api/v1/ai/deals/{deal_id}/forecast — AI-прогноз сделки."""
    return await use_case.execute(DealForecastInput(deal_id=deal_id))


@router.post(
    "/{entity_type}/{entity_id}/next-action",
    response_model=NextBestActionOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Следующее наилучшее действие",
    description=(
        "Определяет наилучшее следующее действие для лида или сделки. "
        "entity_type: 'lead' или 'deal'."
    ),
)
async def next_best_action(
    entity_type: Literal["lead", "deal"],
    entity_id: UUID,
    use_case: GetNextBestActionUseCase = Depends(get_next_best_action_use_case),
) -> NextBestActionOutput:
    """POST /api/v1/ai/{entity_type}/{entity_id}/next-action."""
    data = NextBestActionInput(entity_type=entity_type, entity_id=entity_id)
    return await use_case.execute(data)


@router.post(
    "/leads/{lead_id}/generate-email",
    response_model=GenerateEmailOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Сгенерировать email для лида",
    description=(
        "Создаёт персонализированное email-письмо для лида. "
        "Поддерживает тоны: formal, friendly, assertive."
    ),
)
async def generate_email(
    lead_id: UUID,
    tone: Literal["formal", "friendly", "assertive"] = "friendly",
    extra_context: str | None = None,
    use_case: GenerateEmailUseCase = Depends(get_generate_email_use_case),
) -> GenerateEmailOutput:
    """POST /api/v1/ai/leads/{lead_id}/generate-email — генерация email."""
    data = GenerateEmailInput(
        lead_id=lead_id,
        tone=tone,
        extra_context=extra_context,
    )
    return await use_case.execute(data)
