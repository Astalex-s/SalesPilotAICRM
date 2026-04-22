"""
TelegramService — реализация ITelegramService через python-telegram-bot.

Находится в слое Infrastructure: инкапсулирует работу с Telegram Bot API.
Никакой бизнес-логики, только I/O и маппинг данных.
"""
from __future__ import annotations

import logging

from telegram import Bot, Update
from telegram.error import TelegramError

from src.application.ports.telegram_service import ITelegramService, WebhookInfo

logger = logging.getLogger(__name__)


class TelegramService(ITelegramService):
    """Реализация порта ITelegramService через библиотеку python-telegram-bot.

    Использует Bot напрямую (без Application) для отправки сообщений
    и управления вебхуком. Входящие обновления обрабатываются через process_update.
    """

    def __init__(
        self,
        bot_token: str,
        notification_chat_id: str | int,
    ) -> None:
        """Инициализирует сервис.

        Args:
            bot_token: токен бота из @BotFather (TELEGRAM_BOT_TOKEN).
            notification_chat_id: ID чата для системных уведомлений.
        """
        self._bot_token = bot_token
        self._notification_chat_id = notification_chat_id
        # Ленивая инициализация — Bot создаётся при первом использовании
        self._bot: Bot | None = None

    # ── Публичные методы ───────────────────────────────────────────────────────

    def is_configured(self) -> bool:
        """Возвращает True, если токен и chat_id заданы."""
        return bool(self._bot_token and self._notification_chat_id)

    async def notify(self, text: str) -> None:
        """Отправляет уведомление в преднастроенный чат.

        Args:
            text: текст сообщения (поддерживается HTML-форматирование).

        Вызывает:
            TelegramError: при ошибке Telegram API.
        """
        await self.send_message(self._notification_chat_id, text)

    async def send_message(self, chat_id: str | int, text: str) -> None:
        """Отправляет сообщение в указанный чат.

        Args:
            chat_id: идентификатор чата или username канала (@channel).
            text: текст сообщения (поддерживается HTML-форматирование).

        Вызывает:
            TelegramError: при ошибке Telegram API.
        """
        bot = self._get_bot()
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
            )
            logger.debug("Telegram-сообщение отправлено в чат %s", chat_id)
        except TelegramError:
            logger.exception("Ошибка отправки Telegram-сообщения в чат %s", chat_id)
            raise

    async def set_webhook(self, url: str, secret_token: str | None = None) -> None:
        """Регистрирует URL вебхука в Telegram.

        Args:
            url: HTTPS URL для получения обновлений.
            secret_token: необязательный секрет для валидации запросов.

        Вызывает:
            TelegramError: при ошибке Telegram API.
        """
        bot = self._get_bot()
        kwargs: dict = {"url": url}
        if secret_token:
            kwargs["secret_token"] = secret_token
        await bot.set_webhook(**kwargs)
        logger.info("Telegram вебхук установлен: %s", url)

    async def get_webhook_info(self) -> WebhookInfo:
        """Возвращает информацию о текущем вебхуке.

        Вызывает:
            TelegramError: при ошибке Telegram API.
        """
        bot = self._get_bot()
        info = await bot.get_webhook_info()
        return WebhookInfo(
            url=info.url or "",
            is_set=bool(info.url),
            pending_update_count=info.pending_update_count,
        )

    async def process_update(self, raw_update: dict) -> None:
        """Обрабатывает входящий Update от Telegram.

        Десериализует JSON-объект в Update и логирует полученное событие.
        Расширенная обработка команд добавляется через Application-хэндлеры.

        Args:
            raw_update: десериализованный JSON Telegram Update.
        """
        bot = self._get_bot()
        update = Update.de_json(raw_update, bot)
        if update is None:
            logger.warning("Получен невалидный Telegram update")
            return

        logger.info(
            "Telegram update #%s получен: %s",
            update.update_id,
            _describe_update(update),
        )

    # ── Приватные методы ───────────────────────────────────────────────────────

    def _get_bot(self) -> Bot:
        """Возвращает экземпляр Bot (ленивая инициализация)."""
        if self._bot is None:
            self._bot = Bot(token=self._bot_token)
        return self._bot


# ── Вспомогательные функции ────────────────────────────────────────────────────

def _describe_update(update: Update) -> str:
    """Возвращает краткое описание типа Update для логирования."""
    if update.message:
        return f"message from {update.message.chat_id}"
    if update.callback_query:
        return f"callback_query from {update.callback_query.from_user.id}"
    if update.inline_query:
        return f"inline_query from {update.inline_query.from_user.id}"
    return "unknown update type"
