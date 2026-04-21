"""
DTO для операций с воронками и этапами.
Pydantic-модели — граница валидации на входе и выходе use case.
Нет зависимостей на ORM или FastAPI.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


# ── Входные DTO ────────────────────────────────────────────────────────────────

class GetPipelineInput(BaseModel):
    """Входные данные для получения воронки по ID."""

    pipeline_id: UUID


# ── Выходные DTO ───────────────────────────────────────────────────────────────

class StageOutput(BaseModel):
    """Данные этапа воронки."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pipeline_id: UUID
    name: str
    order: int
    probability: float

    @classmethod
    def from_entity(cls, stage: Stage) -> StageOutput:
        """Маппер: доменная сущность Stage → StageOutput DTO."""
        return cls(
            id=stage.id,
            pipeline_id=stage.pipeline_id,
            name=stage.name,
            order=stage.order,
            probability=stage.probability,
        )


class PipelineOutput(BaseModel):
    """Данные воронки продаж со всеми этапами."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    owner_id: UUID
    stages: list[StageOutput]
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, pipeline: Pipeline) -> PipelineOutput:
        """Маппер: доменная сущность Pipeline → PipelineOutput DTO."""
        return cls(
            id=pipeline.id,
            name=pipeline.name,
            owner_id=pipeline.owner_id,
            stages=[StageOutput.from_entity(s) for s in pipeline.stages],
            is_active=pipeline.is_active,
            created_at=pipeline.created_at,
        )
