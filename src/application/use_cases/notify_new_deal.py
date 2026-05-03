"""
NotifyNewDealUseCase — отправляет Telegram-уведомление при создании новой сделки.
"""
from __future__ import annotations

from src.application.dtos.telegram_dtos import NotifyNewDealInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.ports.telegram_service import ITelegramService


class NotifyNewDealUseCase:
    """Отправляет уведомление о создании сделки в Telegram."""

    def __init__(self, telegram_service: ITelegramService) -> None:
        self._telegram = telegram_service

    async def execute(self, data: NotifyNewDealInput) -> None:
        if not self._telegram.is_configured():
            raise TelegramNotConfiguredError()

        text = (
            "<b>💼 Новая сделка создана</b>\n\n"
            f"📝 <b>{data.deal_title}</b>\n"
            f"👤 Лид: {data.lead_name}\n"
            f"💰 Сумма: {data.value_amount:,.0f} {data.value_currency}"
        )
        await self._telegram.notify(text)
