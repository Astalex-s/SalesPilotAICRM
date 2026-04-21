"""
LeadModel — ORM-модель таблицы leads.
Маппинг: domain entity Lead ↔ SQLAlchemy row.
Бизнес-логики нет — только сериализация/десериализация.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource, LeadStatus
from src.domain.value_objects.phone import Phone
from src.infrastructure.database.base import Base


class LeadModel(Base):
    """ORM-модель для таблицы leads."""

    __tablename__ = "leads"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    owner_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="leadstatus"), nullable=False
    )
    source: Mapped[LeadSource] = mapped_column(
        SAEnum(LeadSource, name="leadsource"), nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    converted_deal_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> Lead:
        """Преобразует ORM-строку в доменную сущность Lead."""
        return Lead(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=Email(self.email),
            owner_id=self.owner_id,
            status=self.status,
            source=self.source,
            phone=Phone(self.phone) if self.phone else None,
            company=self.company,
            notes=self.notes,
            converted_deal_id=self.converted_deal_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, lead: Lead) -> LeadModel:
        """Преобразует доменную сущность Lead в ORM-модель."""
        return cls(
            id=lead.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
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
