"""
Доменная сущность EmailMessage — письмо, связанное с CRM-сущностью.
Хранит полную копию письма (от/кому/тема/тело) и ссылку на лид.
Не зависит от Gmail или любого другого провайдера.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.enums import EmailDirection


@dataclass
class EmailMessage:
    """Письмо, зафиксированное в CRM.

    Инварианты:
    - gmail_message_id уникален в системе
    - subject и from_address не могут быть пустыми
    - link_to_lead() можно вызывать только один раз (если lead_id не задан)
    """

    id: UUID
    gmail_message_id: str       # ID сообщения в Gmail
    gmail_thread_id: str        # ID треда в Gmail
    from_address: str           # адрес отправителя
    to_addresses: list[str]     # список адресатов
    subject: str
    body: str
    direction: EmailDirection
    received_at: datetime
    lead_id: UUID | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.from_address.strip():
            raise ValueError("Адрес отправителя не может быть пустым.")
        if not self.subject.strip():
            raise ValueError("Тема письма не может быть пустой.")
        if not self.to_addresses:
            raise ValueError("Список адресатов не может быть пустым.")

    # ── Фабрики ────────────────────────────────────────────────────────────────

    @classmethod
    def create_outbound(
        cls,
        gmail_message_id: str,
        gmail_thread_id: str,
        to_addresses: list[str],
        from_address: str,
        subject: str,
        body: str,
        received_at: datetime | None = None,
        lead_id: UUID | None = None,
    ) -> EmailMessage:
        """Создаёт исходящее письмо (отправлено менеджером)."""
        return cls(
            id=uuid4(),
            gmail_message_id=gmail_message_id,
            gmail_thread_id=gmail_thread_id,
            from_address=from_address,
            to_addresses=to_addresses,
            subject=subject,
            body=body,
            direction=EmailDirection.OUTBOUND,
            received_at=received_at or datetime.now(timezone.utc),
            lead_id=lead_id,
        )

    @classmethod
    def create_inbound(
        cls,
        gmail_message_id: str,
        gmail_thread_id: str,
        from_address: str,
        to_addresses: list[str],
        subject: str,
        body: str,
        received_at: datetime,
        lead_id: UUID | None = None,
    ) -> EmailMessage:
        """Создаёт входящее письмо (получено от контакта)."""
        return cls(
            id=uuid4(),
            gmail_message_id=gmail_message_id,
            gmail_thread_id=gmail_thread_id,
            from_address=from_address,
            to_addresses=to_addresses,
            subject=subject,
            body=body,
            direction=EmailDirection.INBOUND,
            received_at=received_at,
            lead_id=lead_id,
        )

    # ── Бизнес-операции ────────────────────────────────────────────────────────

    def link_to_lead(self, lead_id: UUID) -> None:
        """Привязывает письмо к лиду.

        Вызывает:
            ValueError: если письмо уже привязано к другому лиду.
        """
        if self.lead_id is not None and self.lead_id != lead_id:
            raise ValueError(
                f"Письмо уже привязано к лиду {self.lead_id}. "
                f"Для смены привязки используйте unlink_from_lead()."
            )
        self.lead_id = lead_id

    def unlink_from_lead(self) -> None:
        """Снимает привязку письма с лида."""
        self.lead_id = None

    def __repr__(self) -> str:
        return (
            f"EmailMessage(id={self.id}, "
            f"subject='{self.subject[:40]}', "
            f"direction={self.direction.value})"
        )
