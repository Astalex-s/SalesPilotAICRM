"""
EmailMessageModel — ORM-модель таблицы email_messages.
Хранит копию письма и ссылку на лид.
Маппинг: domain entity EmailMessage ↔ SQLAlchemy row.
"""
from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.enums import EmailDirection
from src.infrastructure.database.base import Base


class EmailMessageModel(Base):
    """ORM-модель для таблицы email_messages."""

    __tablename__ = "email_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    gmail_message_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    gmail_thread_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    from_address: Mapped[str] = mapped_column(String(320), nullable=False)
    # to_addresses хранится как JSON-массив строк
    to_addresses_json: Mapped[str] = mapped_column(
        Text, nullable=False, name="to_addresses"
    )
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[EmailDirection] = mapped_column(
        SAEnum(EmailDirection, name="emaildirection"), nullable=False
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # FK — nullable, письмо может не быть привязано к лиду
    lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_email_messages_from_received", "from_address", "received_at"),
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> EmailMessage:
        """Преобразует ORM-строку в доменную сущность EmailMessage."""
        return EmailMessage(
            id=self.id,
            gmail_message_id=self.gmail_message_id,
            gmail_thread_id=self.gmail_thread_id,
            from_address=self.from_address,
            to_addresses=json.loads(self.to_addresses_json),
            subject=self.subject,
            body=self.body,
            direction=self.direction,
            received_at=self.received_at,
            lead_id=self.lead_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, message: EmailMessage) -> EmailMessageModel:
        """Преобразует доменную сущность EmailMessage в ORM-модель."""
        return cls(
            id=message.id,
            gmail_message_id=message.gmail_message_id,
            gmail_thread_id=message.gmail_thread_id,
            from_address=message.from_address,
            to_addresses_json=json.dumps(message.to_addresses, ensure_ascii=False),
            subject=message.subject,
            body=message.body,
            direction=message.direction,
            received_at=message.received_at,
            lead_id=message.lead_id,
            created_at=message.created_at,
        )
