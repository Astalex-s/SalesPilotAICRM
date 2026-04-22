"""
NotifyNewLeadUseCase — отправляет Telegram-уведомление при создании нового лида.

Единственная ответственность: сформировать текст уведомления и передать
его в ITelegramService.notify(). Не знает о Telegram API, токенах, chat_id.
"""
from __future__ import annotations

from src.application.dtos.telegram_dtos import NotifyNewLeadInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.ports.telegram_service import ITelegramService


class NotifyNewLeadUseCase:
    """Отправляет уведомление о новом лиде в Telegram."""

    def __init__(self, telegram_service: ITelegramService) -> None:
        # Единственная зависимость — порт уведомлений
        self._telegram = telegram_service

    async def execute(self, data: NotifyNewLeadInput) -> None:
        """Выполняет отправку уведомления.

        Последовательность:
        1. Проверяет, что Telegram настроен — иначе TelegramNotConfiguredError.
        2. Формирует текст сообщения из данных лида.
        3. Отправляет уведомление через ITelegramService.

        Вызывает:
            TelegramNotConfiguredError: если бот не настроен.
        """
        # Шаг 1: проверка конфигурации
        if not self._telegram.is_configured():
            raise TelegramNotConfiguredError()

        # Шаг 2: формирование текста уведомления
        text = (
            "<b>🆕 Новый лид</b>\n\n"
            f"👤 <b>{data.first_name} {data.last_name}</b>\n"
            f"📧 {data.email}\n"
            f"🏢 {data.company or '—'}\n"
            f"📌 Источник: {data.source.value}"
        )

        # Шаг 3: отправка
        await self._telegram.notify(text)
