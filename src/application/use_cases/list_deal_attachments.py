"""
ListDealAttachmentsUseCase — возвращает список вложений для сделки.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.deal_attachment_dtos import DealAttachmentOutput
from src.domain.repositories.deal_attachment_repository import IDealAttachmentRepository


class ListDealAttachmentsUseCase:

    def __init__(self, attachment_repo: IDealAttachmentRepository) -> None:
        self._attachment_repo = attachment_repo

    async def execute(self, deal_id: UUID) -> list[DealAttachmentOutput]:
        attachments = await self._attachment_repo.find_by_deal(deal_id)
        return [DealAttachmentOutput.from_entity(a) for a in attachments]
