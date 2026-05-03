"""
GetEmailThreadUseCase — возвращает все письма конкретного треда.
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import EmailMessageOutput, EmailThreadDetail
from src.domain.repositories.email_message_repository import IEmailMessageRepository


class GetEmailThreadUseCase:
    """Возвращает полный тред с письмами в хронологическом порядке."""

    def __init__(self, email_repo: IEmailMessageRepository) -> None:
        self._email_repo = email_repo

    async def execute(self, thread_id: str) -> EmailThreadDetail:
        """Загружает все письма треда и оборачивает в EmailThreadDetail."""
        messages = await self._email_repo.find_by_thread_id(thread_id)

        subject = messages[0].subject if messages else "(пустой тред)"

        return EmailThreadDetail(
            thread_id=thread_id,
            subject=subject,
            messages=[
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
            ],
        )
