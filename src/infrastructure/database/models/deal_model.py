"""
DealModel — ORM-модель таблицы deals.
Маппинг: domain entity Deal ↔ SQLAlchemy row.
Money value object разделён на два столбца: value_amount, value_currency.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.deal import Deal
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money
from src.infrastructure.database.base import Base


class DealModel(Base):
    """ORM-модель для таблицы deals."""

    __tablename__ = "deals"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    stage_id: Mapped[UUID] = mapped_column(
        ForeignKey("stages.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    pipeline_id: Mapped[UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # Money value object — хранится как (amount, currency)
    value_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    value_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[DealStatus] = mapped_column(
        SAEnum(DealStatus, name="dealstatus", values_callable=lambda e: [x.value for x in e]),
        nullable=False
    )
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_lead_id: Mapped[UUID | None] = mapped_column(nullable=True)
    expected_close_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> Deal:
        """Преобразует ORM-строку в доменную сущность Deal."""
        return Deal(
            id=self.id,
            title=self.title,
            owner_id=self.owner_id,
            stage_id=self.stage_id,
            pipeline_id=self.pipeline_id,
            value=Money(amount=self.value_amount, currency=self.value_currency),
            status=self.status,
            contact_name=self.contact_name,
            company=self.company,
            source_lead_id=self.source_lead_id,
            expected_close_date=self.expected_close_date,
            closed_at=self.closed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, deal: Deal) -> DealModel:
        """Преобразует доменную сущность Deal в ORM-модель."""
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
