"""
StageModel — ORM-модель таблицы stages.
Этапы принадлежат воронке (CASCADE DELETE при удалении Pipeline).
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.stage import Stage
from src.infrastructure.database.base import Base


class StageModel(Base):
    """ORM-модель для таблицы stages."""

    __tablename__ = "stages"
    __table_args__ = (
        # Порядковый номер уникален в пределах воронки
        UniqueConstraint("pipeline_id", "order", name="uq_stage_pipeline_order"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    pipeline_id: Mapped[UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Обратная ссылка на воронку (lazy="noload" — загружается только через PipelineModel)
    pipeline: Mapped["PipelineModel"] = relationship(  # noqa: F821
        "PipelineModel", back_populates="stages"
    )

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> Stage:
        """Преобразует ORM-строку в доменную сущность Stage."""
        return Stage(
            id=self.id,
            pipeline_id=self.pipeline_id,
            name=self.name,
            order=self.order,
            probability=self.probability,
        )

    @classmethod
    def from_entity(cls, stage: Stage) -> StageModel:
        """Преобразует доменную сущность Stage в ORM-модель."""
        return cls(
            id=stage.id,
            pipeline_id=stage.pipeline_id,
            name=stage.name,
            order=stage.order,
            probability=stage.probability,
        )
