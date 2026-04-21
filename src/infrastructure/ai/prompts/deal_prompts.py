"""
Шаблоны промптов для AI-операций над сделками.
"""
from __future__ import annotations

from typing import Any


FORECAST_DEAL_SYSTEM = """\
Ты — AI-аналитик по продажам в B2B CRM.
Твоя задача — спрогнозировать вероятность закрытия сделки и выявить ключевые факторы.
Отвечай ТОЛЬКО валидным JSON без пояснений вне JSON-структуры."""


def forecast_deal_user(deal_context: dict[str, Any]) -> str:
    """Формирует пользовательский промпт для прогноза по сделке."""
    return f"""\
Проанализируй сделку и спрогнозируй вероятность её успешного закрытия.

Данные сделки:
- Название: {deal_context['title']}
- Статус: {deal_context['status']}
- Сумма: {deal_context['value_amount']} {deal_context['value_currency']}
- Контакт: {deal_context['contact_name']}
- Компания: {deal_context['company']}
- Ожидаемая дата закрытия: {deal_context['expected_close_date']}
- Создана: {deal_context['created_at']}

Верни JSON строго в следующем формате:
{{
  "win_probability": <число от 0.0 до 1.0>,
  "risk_factors": ["<риск 1>", "<риск 2>", "<риск 3>"],
  "opportunities": ["<возможность 1>", "<возможность 2>"]
}}"""


NEXT_BEST_ACTION_DEAL_SYSTEM = """\
Ты — AI-коуч для менеджеров по продажам в B2B CRM.
Определи одно конкретное следующее действие для продвижения сделки.
Отвечай ТОЛЬКО валидным JSON без пояснений вне структуры."""
