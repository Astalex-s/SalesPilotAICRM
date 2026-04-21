"""
IEmailMessageRepository — интерфейс репозитория домена для сущности EmailMessage.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.email_message import EmailMessage
from src.domain.repositories.base import BaseRepository


class IEmailMessageRepository(BaseRepository[EmailMessage]):
    """Контракт для операций с хранилищем email-сообщений."""

    @abstractmethod
    async def find_by_gmail_id(self, gmail_message_id: str) -> EmailMessage | None:
        """Возвращает сообщение по Gmail message ID или None."""
        ...

    @abstractmethod
    async def find_by_lead_id(self, lead_id: UUID) -> list[EmailMessage]:
        """Возвращает все письма, привязанные к указанному лиду."""
        ...

    @abstractmethod
    async def find_all(self, limit: int = 50, offset: int = 0) -> list[EmailMessage]:
        """Возвращает письма с пагинацией (от новых к старым)."""
        ...
