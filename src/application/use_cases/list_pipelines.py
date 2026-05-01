"""
ListPipelinesUseCase — получение всех активных воронок.
"""
from __future__ import annotations

from src.application.dtos.pipeline_dtos import PipelineOutput
from src.domain.repositories.pipeline_repository import IPipelineRepository


class ListPipelinesUseCase:
    """Возвращает список всех активных воронок."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self) -> list[PipelineOutput]:
        pipelines = await self._pipeline_repo.find_active()
        return [PipelineOutput.from_entity(p) for p in pipelines]
