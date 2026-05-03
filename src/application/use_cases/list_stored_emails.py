"""
ListStoredEmailsUseCase — возвращает письма из локальной БД без вызова Gmail API.
Используется для отображения инбокса без сетевых задержек.
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import (
    EmailMessageOutput,
    ListStoredEmailsInput,
)
from src.domain.repositories.email_message_repository import IEmailMessageRepository


class ListStoredEmailsUseCase:
    """Возвращает сохранённые письма из БД с пагинацией."""

    def __init__(self, email_repo: IEmailMessageRepository) -> None:
        self._email_repo = email_repo

    async def execute(self, data: ListStoredEmailsInput) -> list[EmailMessageOutput]:
        """Читает письма из БД, без обращения к Gmail API."""
        messages = await self._email_repo.find_all(
            limit=data.limit,
            offset=data.offset,
        )
        return [
            EmailMessageOutput(
                id=m.id,
                gmail_message_id=m.gmail_message_id,
                gmail_thread_id=m.gmail_thread_id,
                from_address=m.from_address,
                to_addresses=m.to_addresses,
                subject=m.subject,
                body=m.body,
                direction=m.direction,
                received_at=m.received_at,
                lead_id=m.lead_id,
                created_at=m.created_at,
            )
            for m in messages
        ]
