"""
NotifyOverdueDealsUseCase — отправляет Telegram-уведомление о просроченных сделках.

Единственная ответственность: найти OPEN-сделки с истёкшим expected_close_date,
сформировать сводное сообщение и отправить через ITelegramService.notify().
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from src.application.exceptions import TelegramNotConfiguredError
from src.application.ports.telegram_service import ITelegramService
from src.domain.repositories.deal_repository import IDealRepository

logger = logging.getLogger(__name__)

# Максимум сделок в одном сообщении, чтобы не превысить лимит Telegram (4096 символов)
_MAX_DEALS_PER_MESSAGE = 20


class NotifyOverdueDealsUseCase:
    """Уведомляет менеджеров о просроченных (overdue) сделках через Telegram."""

    def __init__(
        self,
        telegram_service: ITelegramService,
        deal_repo: IDealRepository,
    ) -> None:
        self._telegram = telegram_service
        self._deal_repo = deal_repo

    async def execute(self) -> int:
        """Находит просроченные сделки и отправляет Telegram-уведомление.

        Returns:
            Количество просроченных сделок.

        Raises:
            TelegramNotConfiguredError: если бот не настроен.
        """
        if not self._telegram.is_configured():
            raise TelegramNotConfiguredError()

        now = datetime.now(timezone.utc)
        overdue = await self._deal_repo.find_overdue(now)

        if not overdue:
            logger.info("NotifyOverdueDeals: просроченных сделок нет")
            return 0

        lines = [f"⚠️ <b>Просроченные сделки ({len(overdue)})</b>\n"]
        for deal in overdue[:_MAX_DEALS_PER_MESSAGE]:
            close_dt = deal.expected_close_date
            if close_dt is not None:
                if close_dt.tzinfo is None:
                    close_dt = close_dt.replace(tzinfo=timezone.utc)
                days_overdue = (now - close_dt).days
                date_str = close_dt.strftime("%d %b")
                overdue_str = f"{days_overdue}д просрочка" if days_overdue > 0 else "сегодня"
            else:
                date_str = "—"
                overdue_str = ""

            lines.append(
                f"• <b>{deal.title}</b>\n"
                f"  💰 {deal.value.amount:,.0f} {deal.value.currency} · "
                f"📅 {date_str} <i>({overdue_str})</i>"
            )

        if len(overdue) > _MAX_DEALS_PER_MESSAGE:
            lines.append(f"\n<i>...и ещё {len(overdue) - _MAX_DEALS_PER_MESSAGE} сделок</i>")

        await self._telegram.notify("\n".join(lines))
        logger.info("NotifyOverdueDeals: отправлено уведомление о %d сделках", len(overdue))
        return len(overdue)
