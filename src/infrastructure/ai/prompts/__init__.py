"""
Модуль шаблонов промптов для AI-сервисов.
Все промпты изолированы здесь — не разбросаны по сервисам.
"""
from src.infrastructure.ai.prompts.deal_prompts import (
    ANALYZE_LOST_DEALS_SYSTEM,
    FORECAST_DEAL_SYSTEM,
    PIPELINE_DIGEST_SYSTEM,
    analyze_lost_deals_user,
    forecast_deal_user,
    pipeline_digest_user,
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
    "ANALYZE_LOST_DEALS_SYSTEM",
    "analyze_lost_deals_user",
    "PIPELINE_DIGEST_SYSTEM",
    "pipeline_digest_user",
]
