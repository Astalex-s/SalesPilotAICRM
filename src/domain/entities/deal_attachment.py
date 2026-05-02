"""
Доменная сущность DealAttachment — файл, прикреплённый к сделке.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class DealAttachment:
    """Файловое вложение, связанное со сделкой.

    Инварианты:
    - filename не может быть пустым
    - size_bytes >= 0
    """

    id: UUID
    deal_id: UUID
    filename: str          # оригинальное имя файла (для отображения)
    storage_path: str      # путь к файлу на диске
    content_type: str
    size_bytes: int
    uploaded_by_id: UUID
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("Имя файла не может быть пустым.")
        if self.size_bytes < 0:
            raise ValueError("Размер файла не может быть отрицательным.")

    @classmethod
    def create(
        cls,
        deal_id: UUID,
        filename: str,
        storage_path: str,
        content_type: str,
        size_bytes: int,
        uploaded_by_id: UUID,
    ) -> DealAttachment:
        return cls(
            id=uuid4(),
            deal_id=deal_id,
            filename=filename.strip(),
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
            uploaded_by_id=uploaded_by_id,
        )
