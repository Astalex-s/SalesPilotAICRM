"""
UpdateStageUseCase — обновление этапа воронки (название, цвет, вероятность).
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.pipeline_dtos import UpdateStageInput, PipelineOutput
from src.application.exceptions import PipelineNotFoundError, StageNotInPipelineError
from src.domain.repositories.pipeline_repository import IPipelineRepository


class UpdateStageUseCase:
    """Обновляет поля существующего этапа воронки."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        self._pipeline_repo = pipeline_repo

    async def execute(
        self, pipeline_id: UUID, stage_id: UUID, data: UpdateStageInput
    ) -> PipelineOutput:
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)

        stage = pipeline.get_stage_by_id(stage_id)
        if stage is None:
            raise StageNotInPipelineError(stage_id, pipeline_id)

        if data.name is not None:
            stage.rename(data.name)
        if data.probability is not None:
            stage.update_probability(data.probability)
        if data.clear_color:
            stage.color = None
        elif data.color is not None:
            stage.color = data.color

        saved = await self._pipeline_repo.save(pipeline)
        return PipelineOutput.from_entity(saved)
