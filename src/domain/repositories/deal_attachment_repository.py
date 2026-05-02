"""
IDealAttachmentRepository — интерфейс репозитория для вложений сделок.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.deal_attachment import DealAttachment
from src.domain.repositories.base import BaseRepository


class IDealAttachmentRepository(BaseRepository[DealAttachment]):

    @abstractmethod
    async def find_by_deal(self, deal_id: UUID) -> list[DealAttachment]:
        """Возвращает все вложения для указанной сделки."""
        ...
