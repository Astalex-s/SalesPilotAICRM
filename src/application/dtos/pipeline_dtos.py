"""
DTO для операций с воронками и этапами.
Pydantic-модели — граница валидации на входе и выходе use case.
Нет зависимостей на ORM или FastAPI.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


# ── Входные DTO — воронки ──────────────────────────────────────────────────────

class GetPipelineInput(BaseModel):
    """Входные данные для получения воронки по ID."""

    pipeline_id: UUID


class CreatePipelineInput(BaseModel):
    """Входные данные для создания новой воронки."""

    name: str = Field(..., min_length=1, max_length=255)


class UpdatePipelineInput(BaseModel):
    """Входные данные для переименования воронки."""

    name: str = Field(..., min_length=1, max_length=255)


# ── Входные DTO — этапы ────────────────────────────────────────────────────────

class AddStageInput(BaseModel):
    """Входные данные для добавления этапа в воронку."""

    name: str = Field(..., min_length=1, max_length=255)
    probability: float = Field(default=0.5, ge=0.0, le=1.0)
    color: str | None = Field(default=None, max_length=20)


class UpdateStageInput(BaseModel):
    """Входные данные для обновления этапа (частичное обновление)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    probability: float | None = Field(default=None, ge=0.0, le=1.0)
    # Пустая строка означает «сбросить цвет»; None означает «не менять»
    color: str | None = Field(default=None, max_length=20)
    clear_color: bool = False  # если True — сбрасывает color в None


# ── Выходные DTO ───────────────────────────────────────────────────────────────

class StageOutput(BaseModel):
    """Данные этапа воронки."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pipeline_id: UUID
    name: str
    order: int
    probability: float
    color: str | None = None

    @classmethod
    def from_entity(cls, stage: Stage) -> StageOutput:
        """Маппер: доменная сущность Stage → StageOutput DTO."""
        return cls(
            id=stage.id,
            pipeline_id=stage.pipeline_id,
            name=stage.name,
            order=stage.order,
            probability=stage.probability,
            color=stage.color,
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
