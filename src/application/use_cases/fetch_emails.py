"""
FetchEmailsUseCase — загрузка писем из Gmail и сохранение в CRM.

Единственная ответственность: получить письма из IEmailService,
отфильтровать уже известные, сохранить новые,
выполнить автопривязку к лидам по адресу отправителя.
"""
from __future__ import annotations

import logging

from src.application.dtos.email_message_dtos import EmailMessageOutput, FetchEmailsInput
from src.application.exceptions import GmailNotAuthorizedError
from src.application.ports.email_service import IEmailService
from src.domain.entities.email_message import EmailMessage
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.lead_repository import ILeadRepository

logger = logging.getLogger(__name__)


class FetchEmailsUseCase:
    """Загружает письма из Gmail и синхронизирует их с CRM."""

    def __init__(
        self,
        email_service: IEmailService,
        email_repo: IEmailMessageRepository,
        lead_repo: ILeadRepository,
    ) -> None:
        self._email_service = email_service
        self._email_repo = email_repo
        self._lead_repo = lead_repo

    async def execute(self, data: FetchEmailsInput) -> list[EmailMessageOutput]:
        """Загружает письма из Gmail.

        Последовательность:
        1. Проверяет авторизацию Gmail.
        2. Получает список FetchedEmail через IEmailService.
        3. Для каждого письма:
           a. Пропускает уже сохранённые (по gmail_message_id).
           b. Создаёт EmailMessage entity (inbound).
           c. Автопривязка: ищет лид по адресу отправителя.
           d. Сохраняет через репозиторий.
        4. Возвращает список DTO сохранённых (новых) писем.

        Вызывает:
            GmailNotAuthorizedError: если OAuth2-токены отсутствуют.
        """
        # Шаг 1: проверка авторизации
        if not await self._email_service.is_authorized():
            raise GmailNotAuthorizedError()

        # Шаг 2: получение из Gmail
        fetched = await self._email_service.fetch_emails(
            query=data.query,
            max_results=data.max_results,
        )

        # Шаг 3: обработка каждого письма
        saved: list[EmailMessage] = []
        for fetched_email in fetched:
            # 3a. Пропускаем дубликаты
            existing = await self._email_repo.find_by_gmail_id(
                fetched_email.gmail_message_id
            )
            if existing is not None:
                logger.debug(
                    "Письмо gmail_id=%s уже в БД — пропускаем.",
                    fetched_email.gmail_message_id,
                )
                continue

            # 3b. Создаём сущность (входящее)
            message = EmailMessage.create_inbound(
                gmail_message_id=fetched_email.gmail_message_id,
                gmail_thread_id=fetched_email.thread_id,
                from_address=fetched_email.from_address,
                to_addresses=fetched_email.to_addresses,
                subject=fetched_email.subject,
                body=fetched_email.body,
                received_at=fetched_email.received_at,
            )

            # 3c. Автопривязка по адресу отправителя (best-effort)
            lead = await self._lead_repo.find_by_email(fetched_email.from_address)
            if lead is not None:
                message.link_to_lead(lead.id)
                logger.debug(
                    "Письмо gmail_id=%s автопривязано к лиду %s.",
                    fetched_email.gmail_message_id,
                    lead.id,
                )

            # 3d. Сохраняем
            message = await self._email_repo.save(message)
            saved.append(message)

        logger.info(
            "FetchEmails: получено %d писем, сохранено %d новых.",
            len(fetched),
            len(saved),
        )

        return [_to_output(m) for m in saved]


def _to_output(message: EmailMessage) -> EmailMessageOutput:
    """Преобразует доменную сущность в выходной DTO."""
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
