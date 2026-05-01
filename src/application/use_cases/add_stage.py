"""
AddStageUseCase — добавление нового этапа в воронку продаж.
Порядковый номер (order) вычисляется автоматически как max(existing) + 1.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.pipeline_dtos import AddStageInput, PipelineOutput
from src.application.exceptions import PipelineNotFoundError
from src.domain.entities.stage import Stage
from src.domain.repositories.pipeline_repository import IPipelineRepository


class AddStageUseCase:
    """Добавляет этап в конец воронки продаж."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(self, pipeline_id: UUID, data: AddStageInput) -> PipelineOutput:
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)

        next_order = (max(s.order for s in pipeline.stages) + 1) if pipeline.stages else 0
        stage = Stage.create(
            pipeline_id=pipeline_id,
            name=data.name,
            order=next_order,
            probability=data.probability,
            color=data.color,
        )
        pipeline.add_stage(stage)
        saved = await self._pipeline_repo.save(pipeline)
        return PipelineOutput.from_entity(saved)
