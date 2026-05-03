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


# ── Batch-анализ потерянных сделок ─────────────────────────────────────────────

ANALYZE_LOST_DEALS_SYSTEM = """\
Ты — AI-аналитик продаж в B2B CRM.
Твоя задача — проанализировать набор проигранных сделок, выявить общие паттерны потерь и
дать конкретные рекомендации для улучшения win rate.
Отвечай ТОЛЬКО валидным JSON без пояснений вне JSON-структуры."""


def analyze_lost_deals_user(deals_context: list[dict[str, Any]]) -> str:
    """Формирует промпт для batch-анализа потерянных сделок."""
    total_value = sum(d.get("value_amount", 0) for d in deals_context)

    deals_list = "\n".join(
        f"{i + 1}. {d.get('title', '—')} | {d.get('company', '—')} | "
        f"{d.get('value_amount', 0)} {d.get('value_currency', 'USD')} | "
        f"этап: {d.get('stage', '—')} | закрыта: {d.get('closed_at', '—')}"
        for i, d in enumerate(deals_context)
    )

    return f"""\
Проанализируй {len(deals_context)} проигранных сделок общей суммой {total_value:.0f}.

Список сделок:
{deals_list}

Выяви общие паттерны потерь и дай рекомендации.

Верни JSON строго в следующем формате:
{{
  "loss_patterns": ["<паттерн 1>", "<паттерн 2>", "<паттерн 3>"],
  "recommendations": ["<рекомендация 1>", "<рекомендация 2>", "<рекомендация 3>"],
  "summary": "<краткое резюме анализа на русском языке, 2-3 предложения>"
}}"""


# ── Еженедельная AI-сводка по воронке ─────────────────────────────────────────

PIPELINE_DIGEST_SYSTEM = """\
Ты — AI-аналитик воронки продаж в B2B CRM.
Твоя задача — сформировать еженедельную сводку по состоянию воронки: выявить риски,
возможности и сделки, требующие первоочередного внимания.
Отвечай ТОЛЬКО валидным JSON без пояснений вне JSON-структуры."""


def pipeline_digest_user(pipeline_context: dict[str, Any]) -> str:
    """Формирует промпт для еженедельного дайджеста воронки."""
    return f"""\
Сформируй еженедельную сводку по воронке продаж.

Данные воронки:
- Название: {pipeline_context.get('pipeline_name', '—')}
- Всего сделок: {pipeline_context.get('total_deals', 0)}
- Открытых: {pipeline_context.get('open_deals', 0)}
- Выигранных: {pipeline_context.get('won_deals', 0)}
- Проигранных: {pipeline_context.get('lost_deals', 0)}
- Общая сумма открытых: {pipeline_context.get('open_value', 0):.0f} {pipeline_context.get('currency', 'USD')}
- Win rate: {pipeline_context.get('win_rate', 0):.1f}%
- Средний чек: {pipeline_context.get('avg_deal_value', 0):.0f}

Распределение по этапам:
{pipeline_context.get('stages_summary', '—')}

Просроченные/застрявшие сделки:
{pipeline_context.get('stale_deals', '—')}

Верни JSON строго в следующем формате:
{{
  "summary": "<общее резюме состояния воронки, 2-3 предложения>",
  "key_metrics": ["<метрика 1>", "<метрика 2>", "<метрика 3>"],
  "risks": ["<риск 1>", "<риск 2>"],
  "opportunities": ["<возможность 1>", "<возможность 2>"],
  "focus_deals": ["<название сделки или рекомендация 1>", "<название сделки или рекомендация 2>"]
}}"""
