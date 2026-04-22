"""
ITelegramService — порт приложения для отправки уведомлений через Telegram Bot API.
Абстракция изолирует бизнес-логику от конкретной реализации (python-telegram-bot).
Реализация (TelegramService) находится в Infrastructure — не здесь.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ── Результирующие структуры данных ────────────────────────────────────────────

@dataclass(frozen=True)
class WebhookInfo:
    """Сведения о текущем вебхуке бота."""

    url: str
    is_set: bool
    pending_update_count: int


# ── Абстрактный интерфейс ──────────────────────────────────────────────────────

class ITelegramService(ABC):
    """Порт для работы с Telegram Bot API.

    Контракт:
    - notify          — отправить уведомление в преднастроенный чат
    - send_message    — отправить сообщение в произвольный чат
    - set_webhook     — зарегистрировать URL вебхука в Telegram
    - get_webhook_info — получить сведения о текущем вебхуке
    - process_update  — обработать входящий Update от Telegram
    - is_configured   — проверить, задан ли токен и chat_id
    """

    @abstractmethod
    async def notify(self, text: str) -> None:
        """Отправляет уведомление в преднастроенный чат (TELEGRAM_NOTIFICATION_CHAT_ID).

        Args:
            text: текст сообщения (поддерживается HTML-форматирование).
        """
        ...

    @abstractmethod
    async def send_message(self, chat_id: str | int, text: str) -> None:
        """Отправляет сообщение в указанный чат.

        Args:
            chat_id: идентификатор чата или username канала.
            text: текст сообщения (поддерживается HTML-форматирование).
        """
        ...

    @abstractmethod
    async def set_webhook(self, url: str, secret_token: str | None = None) -> None:
        """Регистрирует URL вебхука в Telegram.

        Args:
            url: HTTPS URL, на который Telegram будет отправлять обновления.
            secret_token: необязательный токен для валидации входящих запросов.
        """
        ...

    @abstractmethod
    async def get_webhook_info(self) -> WebhookInfo:
        """Возвращает сведения о текущем зарегистрированном вебхуке."""
        ...

    @abstractmethod
    async def process_update(self, raw_update: dict) -> None:
        """Обрабатывает входящий Update, полученный через вебхук.

        Args:
            raw_update: десериализованный JSON-объект Telegram Update.
        """
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Возвращает True, если бот настроен (токен и chat_id заданы)."""
        ...
