"""
DealAttachmentModel — ORM-модель таблицы deal_attachments.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.deal_attachment import DealAttachment
from src.infrastructure.database.base import Base


class DealAttachmentModel(Base):
    __tablename__ = "deal_attachments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    deal_id: Mapped[UUID] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str] = mapped_column(String(200), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_by_id: Mapped[UUID] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_entity(self) -> DealAttachment:
        return DealAttachment(
            id=self.id,
            deal_id=self.deal_id,
            filename=self.filename,
            storage_path=self.storage_path,
            content_type=self.content_type,
            size_bytes=self.size_bytes,
            uploaded_by_id=self.uploaded_by_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, att: DealAttachment) -> DealAttachmentModel:
        return cls(
            id=att.id,
            deal_id=att.deal_id,
            filename=att.filename,
            storage_path=att.storage_path,
            content_type=att.content_type,
            size_bytes=att.size_bytes,
            uploaded_by_id=att.uploaded_by_id,
            created_at=att.created_at,
        )
