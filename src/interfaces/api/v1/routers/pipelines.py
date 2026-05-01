"""
Роутер /api/v1/pipelines — CRUD воронок и их этапов.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.auth_dtos import UserOutput
from src.application.dtos.pipeline_dtos import (
    AddStageInput,
    CreatePipelineInput,
    GetPipelineInput,
    PipelineOutput,
    UpdatePipelineInput,
    UpdateStageInput,
)
from src.application.use_cases.add_stage import AddStageUseCase
from src.application.use_cases.create_pipeline import CreatePipelineUseCase
from src.application.use_cases.delete_pipeline import DeletePipelineUseCase
from src.application.use_cases.delete_stage import DeleteStageUseCase
from src.application.use_cases.get_pipeline import GetPipelineUseCase
from src.application.use_cases.list_pipelines import ListPipelinesUseCase
from src.application.use_cases.update_pipeline import UpdatePipelineUseCase
from src.application.use_cases.update_stage import UpdateStageUseCase
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_add_stage_use_case,
    get_create_pipeline_use_case,
    get_delete_pipeline_use_case,
    get_delete_stage_use_case,
    get_list_pipelines_use_case,
    get_pipeline_use_case,
    get_update_pipeline_use_case,
    get_update_stage_use_case,
)

router = APIRouter(prefix="/pipelines", tags=["Воронки продаж"])


# ── Воронки ────────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[PipelineOutput],
    status_code=status.HTTP_200_OK,
    summary="Список активных воронок",
)
async def list_pipelines(
    use_case: ListPipelinesUseCase = Depends(get_list_pipelines_use_case),
    _: UserOutput = Depends(get_current_user),
) -> list[PipelineOutput]:
    return await use_case.execute()


@router.post(
    "",
    response_model=PipelineOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Создать воронку продаж",
)
async def create_pipeline(
    body: CreatePipelineInput,
    use_case: CreatePipelineUseCase = Depends(get_create_pipeline_use_case),
    current_user: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    return await use_case.execute(body, owner_id=current_user.id)


@router.get(
    "/{pipeline_id}",
    response_model=PipelineOutput,
    status_code=status.HTTP_200_OK,
    summary="Получить воронку продаж",
    description="Возвращает воронку со всеми этапами, упорядоченными по полю order.",
)
async def get_pipeline(
    pipeline_id: UUID,
    use_case: GetPipelineUseCase = Depends(get_pipeline_use_case),
    _: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    data = GetPipelineInput(pipeline_id=pipeline_id)
    return await use_case.execute(data)


@router.patch(
    "/{pipeline_id}",
    response_model=PipelineOutput,
    status_code=status.HTTP_200_OK,
    summary="Переименовать воронку",
)
async def update_pipeline(
    pipeline_id: UUID,
    body: UpdatePipelineInput,
    use_case: UpdatePipelineUseCase = Depends(get_update_pipeline_use_case),
    _: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    return await use_case.execute(pipeline_id, body)


@router.delete(
    "/{pipeline_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить воронку",
)
async def delete_pipeline(
    pipeline_id: UUID,
    use_case: DeletePipelineUseCase = Depends(get_delete_pipeline_use_case),
    _: UserOutput = Depends(get_current_user),
) -> None:
    await use_case.execute(pipeline_id)


# ── Этапы воронки ──────────────────────────────────────────────────────────────

@router.post(
    "/{pipeline_id}/stages",
    response_model=PipelineOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить этап в воронку",
)
async def add_stage(
    pipeline_id: UUID,
    body: AddStageInput,
    use_case: AddStageUseCase = Depends(get_add_stage_use_case),
    _: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    return await use_case.execute(pipeline_id, body)


@router.patch(
    "/{pipeline_id}/stages/{stage_id}",
    response_model=PipelineOutput,
    status_code=status.HTTP_200_OK,
    summary="Обновить этап воронки (название, цвет, вероятность)",
)
async def update_stage(
    pipeline_id: UUID,
    stage_id: UUID,
    body: UpdateStageInput,
    use_case: UpdateStageUseCase = Depends(get_update_stage_use_case),
    _: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    return await use_case.execute(pipeline_id, stage_id, body)


@router.delete(
    "/{pipeline_id}/stages/{stage_id}",
    response_model=PipelineOutput,
    status_code=status.HTTP_200_OK,
    summary="Удалить этап из воронки",
)
async def delete_stage(
    pipeline_id: UUID,
    stage_id: UUID,
    use_case: DeleteStageUseCase = Depends(get_delete_stage_use_case),
    _: UserOutput = Depends(get_current_user),
) -> PipelineOutput:
    return await use_case.execute(pipeline_id, stage_id)
