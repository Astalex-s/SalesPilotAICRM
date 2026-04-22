"""
DTO для операций со сделками.
Pydantic-модели — граница валидации на входе и выходе use case.
Нет зависимостей на ORM или FastAPI.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.deal import Deal
from src.domain.value_objects.enums import DealStatus


# ── Входные DTO ────────────────────────────────────────────────────────────────

class ListDealsInput(BaseModel):
    """Входные данные для получения списка сделок с опциональной фильтрацией."""

    pipeline_id: UUID | None = None
    stage_id: UUID | None = None
    owner_id: UUID | None = None


class ConvertLeadToDealInput(BaseModel):
    """Входные данные для конвертации лида в сделку."""

    lead_id: UUID
    stage_id: UUID
    pipeline_id: UUID
    deal_title: str | None = None
    deal_value_amount: Decimal = Field(default=Decimal("0"), ge=0)
    deal_value_currency: str = Field(default="USD", min_length=3, max_length=3)
    performed_by_id: UUID | None = None


class MoveDealStageInput(BaseModel):
    """Входные данные для перемещения сделки на новый этап."""

    deal_id: UUID
    new_stage_id: UUID
    pipeline_id: UUID
    performed_by_id: UUID


# ── Выходные DTO ───────────────────────────────────────────────────────────────

class DealOutput(BaseModel):
    """Выходные данные сделки, возвращаемые use case."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    owner_id: UUID
    stage_id: UUID
    pipeline_id: UUID
    value_amount: Decimal
    value_currency: str
    status: DealStatus
    contact_name: str | None
    company: str | None
    source_lead_id: UUID | None
    expected_close_date: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, deal: Deal) -> DealOutput:
        """Маппер: доменная сущность Deal → DealOutput DTO."""
        return cls(
            id=deal.id,
            title=deal.title,
            owner_id=deal.owner_id,
            stage_id=deal.stage_id,
            pipeline_id=deal.pipeline_id,
            value_amount=deal.value.amount,
            value_currency=deal.value.currency,
            status=deal.status,
            contact_name=deal.contact_name,
            company=deal.company,
            source_lead_id=deal.source_lead_id,
            expected_close_date=deal.expected_close_date,
            closed_at=deal.closed_at,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
        )
