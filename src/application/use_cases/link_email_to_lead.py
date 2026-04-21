"""
LinkEmailToLeadUseCase — ручная привязка письма к лиду.

Единственная ответственность: загрузить обе сущности,
вызвать email.link_to_lead(), сохранить изменение.
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import (
    EmailMessageOutput,
    LinkEmailToLeadInput,
)
from src.application.exceptions import EmailMessageNotFoundError, LeadNotFoundError
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.lead_repository import ILeadRepository


class LinkEmailToLeadUseCase:
    """Привязывает сохранённое письмо к лиду вручную."""

    def __init__(
        self,
        email_repo: IEmailMessageRepository,
        lead_repo: ILeadRepository,
    ) -> None:
        self._email_repo = email_repo
        self._lead_repo = lead_repo

    async def execute(self, data: LinkEmailToLeadInput) -> EmailMessageOutput:
        """Выполняет привязку письма к лиду.

        Последовательность:
        1. Загружает EmailMessage — EmailMessageNotFoundError если не найдено.
        2. Загружает Lead — LeadNotFoundError если не найден.
        3. Вызывает email.link_to_lead(lead_id).
        4. Сохраняет изменение через репозиторий.
        5. Возвращает EmailMessageOutput.

        Вызывает:
            EmailMessageNotFoundError: письмо с email_message_id не найдено.
            LeadNotFoundError: лид с lead_id не найден.
            ValueError: письмо уже привязано к другому лиду.
        """
        # Шаг 1: загрузка письма
        message = await self._email_repo.get_by_id(data.email_message_id)
        if message is None:
            raise EmailMessageNotFoundError(data.email_message_id)

        # Шаг 2: проверка существования лида
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)

        # Шаг 3: привязка (доменная операция — может выбросить ValueError)
        message.link_to_lead(data.lead_id)

        # Шаг 4: сохранение
        message = await self._email_repo.save(message)

        # Шаг 5: формирование DTO
        return EmailMessageOutput(
            id=message.id,
            gmail_message_id=message.gmail_message_id,
            gmail_thread_id=message.gmail_thread_id,
            from_address=message.from_address,
            to_addresses=message.to_addresses,
            subject=message.subject,
            body=message.body,
            direction=message.direction,
            received_at=message.received_at,
            lead_id=message.lead_id,
            created_at=message.created_at,
        )
