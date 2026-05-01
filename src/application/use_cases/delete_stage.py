"""
DeleteStageUseCase — удаление этапа из воронки продаж.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.pipeline_dtos import PipelineOutput
from src.application.exceptions import PipelineNotFoundError
from src.domain.repositories.pipeline_repository import IPipelineRepository


class DeleteStageUseCase:
    """Удаляет этап из воронки. Порядок оставшихся этапов сохраняется."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self, pipeline_id: UUID, stage_id: UUID) -> PipelineOutput:
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)

        # remove_stage raises StageNotFoundError (DomainError) if stage absent —
        # caught by handle_domain_error → HTTP 422
        pipeline.remove_stage(stage_id)
        saved = await self._pipeline_repo.save(pipeline)
        return PipelineOutput.from_entity(saved)
