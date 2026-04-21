"""
SqlEmailMessageRepository — реализация IEmailMessageRepository на SQLAlchemy 2.0 async.
Только I/O: SQL-запросы и маппинг. Никакой бизнес-логики.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.email_message import EmailMessage
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.infrastructure.database.models.email_message_model import EmailMessageModel


class SqlEmailMessageRepository(IEmailMessageRepository):
    """Реализация IEmailMessageRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> EmailMessage | None:
        """Возвращает письмо по UUID или None."""
        row = await self._session.get(EmailMessageModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: EmailMessage) -> EmailMessage:
        """Выполняет upsert письма и возвращает актуальное состояние."""
        orm = EmailMessageModel.from_entity(entity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, entity_id: UUID) -> None:
        """Удаляет письмо по UUID."""
        row = await self._session.get(EmailMessageModel, entity_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_by_gmail_id(self, gmail_message_id: str) -> EmailMessage | None:
        """Возвращает письмо по Gmail message ID (уникальный индекс) или None."""
        stmt = (
            select(EmailMessageModel)
            .where(EmailMessageModel.gmail_message_id == gmail_message_id)
            .limit(1)
        )
        rows = await self._session.scalars(stmt)
        row = rows.first()
        return row.to_entity() if row is not None else None

    async def find_by_lead_id(self, lead_id: UUID) -> list[EmailMessage]:
        """Возвращает все письма, привязанные к указанному лиду (новые первыми)."""
        stmt = (
            select(EmailMessageModel)
            .where(EmailMessageModel.lead_id == lead_id)
            .order_by(EmailMessageModel.received_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_all(self, limit: int = 50, offset: int = 0) -> list[EmailMessage]:
        """Возвращает письма с пагинацией (новые первыми)."""
        stmt = (
            select(EmailMessageModel)
            .order_by(EmailMessageModel.received_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
