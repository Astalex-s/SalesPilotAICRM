"""
Шаблоны промптов для AI-операций над лидами.
Изолированы от бизнес-логики — только форматирование строк.
Изменение промпта не требует правок в use cases или сервисе.
"""
from __future__ import annotations

from typing import Any


SCORE_LEAD_SYSTEM = """\
Ты — AI-аналитик CRM-системы для B2B-продаж.
Твоя задача — объективно оценить лида и вернуть результат строго в формате JSON.
Отвечай ТОЛЬКО валидным JSON без каких-либо пояснений вне JSON-структуры."""


def score_lead_user(lead_context: dict[str, Any]) -> str:
    """Формирует пользовательский промпт для оценки лида."""
    return f"""\
Оцени следующего лида по вероятности конвертации в сделку (0.0 — нет шансов, 1.0 — точно конвертируется).

Данные лида:
- Имя: {lead_context['name']}
- Email: {lead_context['email']}
- Компания: {lead_context['company']}
- Источник: {lead_context['source']}
- Текущий статус: {lead_context['status']}
- Телефон: {lead_context.get('phone') or 'Не указан'}
- Заметки: {lead_context['notes']}

Верни JSON строго в следующем формате:
{{
  "score": <число от 0.0 до 1.0>,
  "reasoning": "<обоснование оценки на русском языке, 2-3 предложения>",
  "recommended_actions": ["<действие 1>", "<действие 2>", "<действие 3>"]
}}"""


NEXT_BEST_ACTION_LEAD_SYSTEM = """\
Ты — AI-коуч для менеджеров по продажам в B2B CRM.
Определи одно конкретное следующее действие для работы с лидом.
Отвечай ТОЛЬКО валидным JSON без пояснений вне структуры."""


def next_best_action_user(entity_context: dict[str, Any]) -> str:
    """Формирует промпт для определения следующего действия."""
    entity_type = entity_context.get("entity_type", "lead")
    label = "лида" if entity_type == "lead" else "сделки"
    return f"""\
Определи наилучшее следующее действие для работы с {label}.

Данные:
{_format_context(entity_context)}

Верни JSON строго в следующем формате:
{{
  "action": "<конкретное, выполнимое действие>",
  "priority": "<high|medium|low>",
  "reasoning": "<обоснование на русском языке, 1-2 предложения>"
}}"""


def _format_context(ctx: dict[str, Any]) -> str:
    """Форматирует словарь контекста в читаемый список."""
    return "\n".join(
        f"- {key.replace('_', ' ').capitalize()}: {value}"
        for key, value in ctx.items()
        if key != "entity_type"
    )
