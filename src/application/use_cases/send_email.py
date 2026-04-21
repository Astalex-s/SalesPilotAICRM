"""
SendEmailUseCase — отправка письма через Gmail и запись в CRM.

Единственная ответственность: принять данные, отправить через IEmailService,
сохранить EmailMessage, опционально привязать к лиду, залогировать активность.
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import EmailMessageOutput, SendEmailInput
from src.application.exceptions import GmailNotAuthorizedError, LeadNotFoundError
from src.application.ports.email_service import IEmailService
from src.domain.entities.activity import Activity
from src.domain.entities.email_message import EmailMessage
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.enums import ActivityType


class SendEmailUseCase:
    """Отправляет письмо через Gmail и фиксирует его в CRM-системе."""

    def __init__(
        self,
        email_service: IEmailService,
        email_repo: IEmailMessageRepository,
        lead_repo: ILeadRepository,
        activity_repo: IActivityRepository,
    ) -> None:
        self._email_service = email_service
        self._email_repo = email_repo
        self._lead_repo = lead_repo
        self._activity_repo = activity_repo

    async def execute(self, data: SendEmailInput) -> EmailMessageOutput:
        """Выполняет отправку письма.

        Последовательность:
        1. Проверяет авторизацию Gmail.
        2. Если указан lead_id — проверяет существование лида.
        3. Вызывает IEmailService.send_email().
        4. Создаёт и сохраняет EmailMessage (outbound).
        5. Если указан lead_id — логирует активность EMAIL.
        6. Возвращает EmailMessageOutput.

        Вызывает:
            GmailNotAuthorizedError: если OAuth2-токены отсутствуют.
            LeadNotFoundError: если lead_id указан, но лид не найден.
        """
        # Шаг 1: проверка авторизации
        if not await self._email_service.is_authorized():
            raise GmailNotAuthorizedError()

        # Шаг 2: проверка лида (если указан)
        if data.lead_id is not None:
            lead = await self._lead_repo.get_by_id(data.lead_id)
            if lead is None:
                raise LeadNotFoundError(data.lead_id)

        # Шаг 3: отправка через провайдера
        result = await self._email_service.send_email(
            to=data.to,
            subject=data.subject,
            body=data.body,
            thread_id=data.thread_id,
        )

        # Шаг 4: создание и сохранение доменной сущности
        message = EmailMessage.create_outbound(
            gmail_message_id=result.gmail_message_id,
            gmail_thread_id=result.thread_id,
            from_address="me",  # Gmail API возвращает "me" для своего ящика
            to_addresses=[data.to],
            subject=data.subject,
            body=data.body,
            lead_id=data.lead_id,
        )
        message = await self._email_repo.save(message)

        # Шаг 5: запись активности EMAIL на лида
        if data.lead_id is not None:
            activity = Activity.create(
                entity_type="lead",
                entity_id=data.lead_id,
                activity_type=ActivityType.EMAIL,
                performed_by_id=data.performed_by_id,
                body=f"Отправлено письмо: '{data.subject}' → {data.to}",
            )
            await self._activity_repo.save(activity)

        # Шаг 6: формирование DTO
        return _to_output(message)


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
