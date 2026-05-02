"""
DeleteDealAttachmentUseCase — удаляет файл с диска и запись из БД.
"""
from __future__ import annotations

import os
import logging
from uuid import UUID

from src.domain.repositories.deal_attachment_repository import IDealAttachmentRepository

logger = logging.getLogger(__name__)


class DeleteDealAttachmentUseCase:

    def __init__(self, attachment_repo: IDealAttachmentRepository) -> None:
        self._attachment_repo = attachment_repo

    async def execute(self, attachment_id: UUID) -> None:
        att = await self._attachment_repo.get_by_id(attachment_id)
        if att is None:
            return  # идемпотентно — уже удалено

        # Удаляем файл с диска (ошибки только логируем — не прерываем)
        try:
            if os.path.exists(att.storage_path):
                os.remove(att.storage_path)
        except OSError:
            logger.warning("Не удалось удалить файл %s", att.storage_path)

        await self._attachment_repo.delete(attachment_id)
