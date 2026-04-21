"""
GetPipelineUseCase — use case получения воронки продаж по ID.

Единственная ответственность: найти воронку в хранилище и вернуть DTO.
"""
from __future__ import annotations

from src.application.dtos.pipeline_dtos import GetPipelineInput, PipelineOutput
from src.application.exceptions import PipelineNotFoundError
from src.domain.repositories.pipeline_repository import IPipelineRepository


class GetPipelineUseCase:
    """Возвращает воронку продаж со всеми этапами по её ID."""

    def __init__(self, pipeline_repo: IPipelineRepository) -> None:
        # Репозиторий воронок — единственная зависимость
        self._pipeline_repo = pipeline_repo

    async def execute(self, data: GetPipelineInput) -> PipelineOutput:
        """Выполняет получение воронки.

        Последовательность:
        1. Ищет воронку по ID.
        2. Выбрасывает PipelineNotFoundError, если воронка не найдена.
        3. Возвращает DTO с воронкой и всеми её этапами.

        Вызывает:
            PipelineNotFoundError: Если воронка с указанным ID не существует.
        """
        pipeline = await self._pipeline_repo.get_by_id(data.pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(data.pipeline_id)

        return PipelineOutput.from_entity(pipeline)
