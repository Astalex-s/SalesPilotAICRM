"""
HandleBotCommandUseCase — обрабатывает команды Telegram-бота (/leads, /deals).

Единственная ответственность: разобрать входящий Update, определить команду,
запросить данные из репозиториев и отправить форматированный ответ в тот же чат.
"""
from __future__ import annotations

import logging

from src.application.ports.telegram_service import ITelegramService
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository

logger = logging.getLogger(__name__)

_MAX_ITEMS = 10


class HandleBotCommandUseCase:
    """Обрабатывает входящие команды бота и отвечает в чат."""

    def __init__(
        self,
        telegram_service: ITelegramService,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
    ) -> None:
        self._telegram = telegram_service
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo

    async def execute(self, raw_update: dict) -> None:
        """Разбирает Update и вызывает нужный обработчик команды.

        Поддерживаемые команды: /leads, /deals.
        Неизвестные команды игнорируются без ответа.
        """
        message: dict = raw_update.get("message") or {}
        text: str = message.get("text") or ""
        chat_id: int | None = (message.get("chat") or {}).get("id")

        if not chat_id or not text.startswith("/"):
            return

        command = text.split()[0].lower().split("@")[0]  # strip @botname suffix

        if command == "/leads":
            await self._handle_leads(chat_id)
        elif command == "/deals":
            await self._handle_deals(chat_id)
        else:
            logger.debug("Неизвестная команда бота: %s", command)

    # ── Обработчики команд ────────────────────────────────────────────────────

    async def _handle_leads(self, chat_id: int) -> None:
        leads = await self._lead_repo.find_all()
        # Последние N по дате создания
        leads = sorted(leads, key=lambda l: l.created_at, reverse=True)[:_MAX_ITEMS]

        if not leads:
            await self._telegram.send_message(chat_id, "📋 <b>Лиды</b>\n\nЛиды не найдены.")
            return

        lines = [f"📋 <b>Лиды (последние {len(leads)})</b>\n"]
        for i, lead in enumerate(leads, 1):
            company = f" · {lead.company}" if lead.company else ""
            lines.append(
                f"{i}. <b>{lead.first_name} {lead.last_name}</b>{company}\n"
                f"   {lead.status.value.upper()} · {lead.email.value}"
            )

        await self._telegram.send_message(chat_id, "\n".join(lines))

    async def _handle_deals(self, chat_id: int) -> None:
        deals = await self._deal_repo.find_all()
        # Последние N по дате создания
        deals = sorted(deals, key=lambda d: d.created_at, reverse=True)[:_MAX_ITEMS]

        if not deals:
            await self._telegram.send_message(chat_id, "💼 <b>Сделки</b>\n\nСделок не найдено.")
            return

        lines = [f"💼 <b>Сделки (последние {len(deals)})</b>\n"]
        for i, deal in enumerate(deals, 1):
            lines.append(
                f"{i}. <b>{deal.title}</b>\n"
                f"   {deal.status.value.upper()} · "
                f"{deal.value.amount:,.0f} {deal.value.currency}"
            )

        await self._telegram.send_message(chat_id, "\n".join(lines))
