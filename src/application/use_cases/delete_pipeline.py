"""
DeletePipelineUseCase — удаление воронки продаж (каскадно удаляет этапы).
"""
from __future__ import annotations

from uuid import UUID

from src.application.exceptions import PipelineNotFoundError
from src.domain.repositories.pipeline_repository import IPipelineRepository


class DeletePipelineUseCase:
    """Удаляет воронку и все её этапы."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self, pipeline_id: UUID) -> None:
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)
        await self._pipeline_repo.delete(pipeline_id)
