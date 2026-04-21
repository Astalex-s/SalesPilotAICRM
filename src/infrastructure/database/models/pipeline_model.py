"""
PipelineModel — ORM-модель таблицы pipelines.
Владеет коллекцией StageModel через relationship (cascade delete).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.pipeline import Pipeline
from src.infrastructure.database.base import Base


class PipelineModel(Base):
    """ORM-модель для таблицы pipelines."""

    __tablename__ = "pipelines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Этапы загружаются вместе с воронкой (selectin избегает N+1 запросов)
    stages: Mapped[list["StageModel"]] = relationship(  # noqa: F821
        "StageModel",
        back_populates="pipeline",
        order_by="StageModel.order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> Pipeline:
        """Преобразует ORM-строку (с загруженными этапами) в Pipeline."""
        return Pipeline(
            id=self.id,
            name=self.name,
            owner_id=self.owner_id,
            is_active=self.is_active,
            created_at=self.created_at,
            stages=[s.to_entity() for s in self.stages],
        )

    @classmethod
    def from_entity(cls, pipeline: Pipeline) -> PipelineModel:
        """Преобразует доменную сущность Pipeline в ORM-модель (без этапов)."""
        return cls(
            id=pipeline.id,
            name=pipeline.name,
            owner_id=pipeline.owner_id,
            is_active=pipeline.is_active,
            created_at=pipeline.created_at,
        )
