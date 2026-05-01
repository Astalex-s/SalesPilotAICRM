"""
CreatePipelineUseCase — создание новой воронки продаж.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.pipeline_dtos import CreatePipelineInput, PipelineOutput
from src.domain.entities.pipeline import Pipeline
from src.domain.repositories.pipeline_repository import IPipelineRepository


class CreatePipelineUseCase:
    """Создаёт новую пустую воронку продаж."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self, data: CreatePipelineInput, owner_id: UUID) -> PipelineOutput:
        pipeline = Pipeline.create(name=data.name, owner_id=owner_id)
        saved = await self._pipeline_repo.save(pipeline)
        return PipelineOutput.from_entity(saved)
