"""
Модуль шаблонов промптов для AI-сервисов.
Все промпты изолированы здесь — не разбросаны по сервисам.
"""
from src.infrastructure.ai.prompts.deal_prompts import (
    FORECAST_DEAL_SYSTEM,
    forecast_deal_user,
)
from src.infrastructure.ai.prompts.email_prompts import (
    GENERATE_EMAIL_SYSTEM,
    generate_email_user,
)
from src.infrastructure.ai.prompts.lead_prompts import (
    NEXT_BEST_ACTION_LEAD_SYSTEM,
    SCORE_LEAD_SYSTEM,
    next_best_action_user,
    score_lead_user,
)

__all__ = [
    "SCORE_LEAD_SYSTEM",
    "score_lead_user",
    "FORECAST_DEAL_SYSTEM",
    "forecast_deal_user",
    "NEXT_BEST_ACTION_LEAD_SYSTEM",
    "next_best_action_user",
    "GENERATE_EMAIL_SYSTEM",
    "generate_email_user",
]
