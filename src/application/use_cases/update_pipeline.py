"""
UpdatePipelineUseCase — переименование воронки продаж.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.pipeline_dtos import UpdatePipelineInput, PipelineOutput
from src.application.exceptions import PipelineNotFoundError
from src.domain.repositories.pipeline_repository import IPipelineRepository


class UpdatePipelineUseCase:
    """Переименовывает воронку продаж."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self, pipeline_id: UUID, data: UpdatePipelineInput) -> PipelineOutput:
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)

        pipeline.name = data.name.strip()
        saved = await self._pipeline_repo.save(pipeline)
        return PipelineOutput.from_entity(saved)
