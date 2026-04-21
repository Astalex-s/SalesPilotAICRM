"""
DTO для операций с лидами.
Pydantic-модели используются как граница валидации на входе и выходе use case.
Нет зависимостей на ORM или FastAPI.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.entities.lead import Lead
from src.domain.value_objects.enums import LeadSource, LeadStatus


# ── Входные DTO ────────────────────────────────────────────────────────────────

class ListLeadsInput(BaseModel):
    """Параметры фильтрации для списка лидов."""

    owner_id: UUID | None = None
    status: LeadStatus | None = None


class CreateLeadInput(BaseModel):
    """Входные данные для создания нового лида."""

    first_name: str
    last_name: str
    email: str
    owner_id: UUID
    source: LeadSource = LeadSource.OTHER
    phone: str | None = None
    company: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Поле не может быть пустым.")
        return v.strip()


# ── Выходные DTO ───────────────────────────────────────────────────────────────

class LeadOutput(BaseModel):
    """Выходные данные лида, возвращаемые use case."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    full_name: str
    email: str
    owner_id: UUID
    status: LeadStatus
    source: LeadSource
    phone: str | None
    company: str | None
    notes: str | None
    converted_deal_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, lead: Lead) -> LeadOutput:
        """Маппер: доменная сущность Lead → LeadOutput DTO."""
        return cls(
            id=lead.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            full_name=lead.full_name,
            email=str(lead.email),
            owner_id=lead.owner_id,
            status=lead.status,
            source=lead.source,
            phone=str(lead.phone) if lead.phone else None,
            company=lead.company,
            notes=lead.notes,
            converted_deal_id=lead.converted_deal_id,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
