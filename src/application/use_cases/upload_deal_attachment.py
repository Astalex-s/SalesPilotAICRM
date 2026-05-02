"""
UploadDealAttachmentUseCase — сохраняет файл на диск и записывает метаданные в БД.
"""
from __future__ import annotations

import os
from uuid import UUID

from src.application.dtos.deal_attachment_dtos import DealAttachmentOutput
from src.application.exceptions import DealNotFoundError
from src.domain.entities.deal_attachment import DealAttachment
from src.domain.repositories.deal_attachment_repository import IDealAttachmentRepository
from src.domain.repositories.deal_repository import IDealRepository

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class UploadDealAttachmentUseCase:

    def __init__(
        self,
        deal_repo: IDealRepository,
        attachment_repo: IDealAttachmentRepository,
        uploads_dir: str,
    ) -> None:
        self._deal_repo = deal_repo
        self._attachment_repo = attachment_repo
        self._uploads_dir = uploads_dir

    async def execute(
        self,
        deal_id: UUID,
        filename: str,
        content_type: str,
        file_data: bytes,
        uploaded_by_id: UUID,
    ) -> DealAttachmentOutput:
        if len(file_data) > MAX_FILE_SIZE:
            raise ValueError(f"Файл превышает максимальный размер {MAX_FILE_SIZE // (1024*1024)} МБ.")

        deal = await self._deal_repo.get_by_id(deal_id)
        if deal is None:
            raise DealNotFoundError(deal_id)

        # Создаём директорию для сделки
        deal_dir = os.path.join(self._uploads_dir, "deals", str(deal_id))
        os.makedirs(deal_dir, exist_ok=True)

        # Генерируем сущность до записи файла — используем её id для имени файла
        att = DealAttachment.create(
            deal_id=deal_id,
            filename=filename,
            storage_path="",  # заполним ниже
            content_type=content_type,
            size_bytes=len(file_data),
            uploaded_by_id=uploaded_by_id,
        )

        # Имя файла на диске: {att.id}_{original_name} — гарантирует уникальность
        safe_filename = f"{att.id}_{filename}"
        storage_path = os.path.join(deal_dir, safe_filename)
        att.storage_path = storage_path

        # Запись файла
        with open(storage_path, "wb") as f:
            f.write(file_data)

        saved = await self._attachment_repo.save(att)
        return DealAttachmentOutput.from_entity(saved)
