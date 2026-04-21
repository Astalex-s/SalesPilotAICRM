"""
Роутер /api/v1/deals.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.deal_dtos import ConvertLeadToDealInput, DealOutput, MoveDealStageInput
from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.interfaces.api.dependencies import (
    get_convert_lead_use_case,
    get_move_deal_stage_use_case,
)
from src.interfaces.schemas.deal_schemas import MoveDealStageRequest

router = APIRouter(prefix="/deals", tags=["Сделки"])


@router.post(
    "",
    response_model=DealOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Конвертировать лида в сделку",
    description=(
        "Конвертирует квалифицированного лида в сделку. "
        "Лид должен иметь статус QUALIFIED. "
        "Указанный этап должен принадлежать указанной воронке."
    ),
)
async def convert_lead_to_deal(
    body: ConvertLeadToDealInput,
    use_case: ConvertLeadToDealUseCase = Depends(get_convert_lead_use_case),
) -> DealOutput:
    """POST /api/v1/deals — создание сделки из квалифицированного лида."""
    return await use_case.execute(body)


@router.patch(
    "/{deal_id}/stage",
    response_model=DealOutput,
    status_code=status.HTTP_200_OK,
    summary="Переместить сделку на новый этап",
    description=(
        "Перемещает открытую сделку на другой этап внутри той же воронки. "
        "Закрытые сделки (WON/LOST) переместить нельзя."
    ),
)
async def move_deal_stage(
    deal_id: UUID,
    body: MoveDealStageRequest,
    use_case: MoveDealStageUseCase = Depends(get_move_deal_stage_use_case),
) -> DealOutput:
    """PATCH /api/v1/deals/{deal_id}/stage — смена этапа сделки."""
    # Контроллер собирает application DTO из path-параметра и тела запроса
    data = MoveDealStageInput(
        deal_id=deal_id,
        new_stage_id=body.new_stage_id,
        pipeline_id=body.pipeline_id,
        performed_by_id=body.performed_by_id,
    )
    return await use_case.execute(data)
