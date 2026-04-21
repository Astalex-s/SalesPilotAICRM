"""
Шаблоны промптов для AI-генерации email-писем.
"""
from __future__ import annotations

from typing import Any


GENERATE_EMAIL_SYSTEM = """\
Ты — AI-копирайтер для B2B-продаж.
Твоя задача — написать персонализированное email-письмо менеджера потенциальному клиенту.
Письмо должно быть профессиональным, конкретным и побуждать к ответу.
Отвечай ТОЛЬКО валидным JSON без пояснений вне JSON-структуры."""

_TONE_DESCRIPTIONS = {
    "formal": "официальный, деловой стиль, обращение на «Вы»",
    "friendly": "дружелюбный, тёплый стиль, обращение на «Вы» но без излишней формальности",
    "assertive": "уверенный, прямой стиль с акцентом на ценность предложения",
}


def generate_email_user(
    lead_context: dict[str, Any],
    tone: str,
    extra_context: str | None,
) -> str:
    """Формирует промпт для генерации email-письма."""
    tone_desc = _TONE_DESCRIPTIONS.get(tone, tone)
    extra = f"\nДополнительный контекст от менеджера: {extra_context}" if extra_context else ""

    return f"""\
Напиши персонализированное email-письмо для следующего лида.

Данные лида:
- Имя: {lead_context['name']}
- Имя (для обращения): {lead_context['first_name']}
- Компания: {lead_context['company']}
- Источник: {lead_context['source']}
- Статус: {lead_context['status']}
- Заметки: {lead_context['notes']}{extra}

Требования к письму:
- Тон: {tone_desc}
- Язык: русский
- Длина тела: 3-5 абзацев
- Должно содержать чёткий призыв к действию (CTA)

Верни JSON строго в следующем формате:
{{
  "subject": "<тема письма>",
  "body": "<полный текст письма>"
}}"""
