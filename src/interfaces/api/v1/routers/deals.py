"""
Роутер /api/v1/deals.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.application.dtos.deal_dtos import ConvertLeadToDealInput, DealOutput, MoveDealStageInput
from src.application.dtos.telegram_dtos import NotifyDealStageChangeInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.application.use_cases.notify_deal_stage_change import NotifyDealStageChangeUseCase
from src.interfaces.api.dependencies import (
    get_convert_lead_use_case,
    get_move_deal_stage_use_case,
    get_notify_deal_stage_change_use_case,
)
from src.interfaces.schemas.deal_schemas import MoveDealStageRequest

logger = logging.getLogger(__name__)

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
    background_tasks: BackgroundTasks,
    use_case: MoveDealStageUseCase = Depends(get_move_deal_stage_use_case),
    notify_use_case: NotifyDealStageChangeUseCase = Depends(get_notify_deal_stage_change_use_case),
) -> DealOutput:
    """PATCH /api/v1/deals/{deal_id}/stage — смена этапа сделки."""
    data = MoveDealStageInput(
        deal_id=deal_id,
        new_stage_id=body.new_stage_id,
        pipeline_id=body.pipeline_id,
        performed_by_id=body.performed_by_id,
    )
    result = await use_case.execute(data)

    # Фоновое уведомление — не блокирует ответ клиенту
    background_tasks.add_task(
        _send_deal_stage_notification,
        notify_use_case,
        result,
        body.new_stage_id,
    )

    return result


# ── Фоновые задачи ─────────────────────────────────────────────────────────────

async def _send_deal_stage_notification(
    use_case: NotifyDealStageChangeUseCase,
    deal: DealOutput,
    new_stage_id: UUID,
) -> None:
    """Отправляет Telegram-уведомление о смене этапа сделки в фоне.

    Ошибки конфигурации и транспорта не прерывают основной поток — только логируются.
    """
    try:
        data = NotifyDealStageChangeInput(
            deal_id=deal.id,
            deal_title=deal.title,
            new_stage_id=new_stage_id,
            pipeline_id=deal.pipeline_id,
        )
        await use_case.execute(data)
    except TelegramNotConfiguredError:
        # Telegram не настроен — молча пропускаем
        pass
    except Exception:
        logger.exception(
            "Ошибка отправки Telegram-уведомления о смене этапа сделки %s", deal.id
        )
