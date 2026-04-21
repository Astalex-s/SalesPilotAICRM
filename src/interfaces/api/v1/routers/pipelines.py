"""
Роутер /api/v1/pipelines.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.pipeline_dtos import GetPipelineInput, PipelineOutput
from src.application.use_cases.get_pipeline import GetPipelineUseCase
from src.interfaces.api.dependencies import get_pipeline_use_case

router = APIRouter(prefix="/pipelines", tags=["Воронки продаж"])


@router.get(
    "/{pipeline_id}",
    response_model=PipelineOutput,
    status_code=status.HTTP_200_OK,
    summary="Получить воронку продаж",
    description="Возвращает воронку продаж со всеми её этапами, упорядоченными по полю order.",
)
async def get_pipeline(
    pipeline_id: UUID,
    use_case: GetPipelineUseCase = Depends(get_pipeline_use_case),
) -> PipelineOutput:
    """GET /api/v1/pipelines/{pipeline_id} — получение воронки по ID."""
    data = GetPipelineInput(pipeline_id=pipeline_id)
    return await use_case.execute(data)
