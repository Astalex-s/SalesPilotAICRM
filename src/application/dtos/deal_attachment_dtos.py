"""
DTO для операций с вложениями сделок.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.entities.deal_attachment import DealAttachment


class DealAttachmentOutput(BaseModel):
    id: UUID
    deal_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    uploaded_by_id: UUID
    created_at: datetime

    @classmethod
    def from_entity(cls, att: DealAttachment) -> DealAttachmentOutput:
        return cls(
            id=att.id,
            deal_id=att.deal_id,
            filename=att.filename,
            content_type=att.content_type,
            size_bytes=att.size_bytes,
            uploaded_by_id=att.uploaded_by_id,
            created_at=att.created_at,
        )
