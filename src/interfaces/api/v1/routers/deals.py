"""
Роутер /api/v1/deals.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from src.application.dtos.deal_dtos import CloseDealInput, ConvertLeadToDealInput, DealOutput, ListDealsInput, MoveDealStageInput
from src.application.dtos.telegram_dtos import NotifyDealStageChangeInput
from src.application.exceptions import DealNotFoundError, TelegramNotConfiguredError
from src.domain.exceptions import DealAlreadyClosedError
from src.application.use_cases.close_deal import CloseDealUseCase
from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.application.use_cases.list_deals import ListDealsUseCase
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.application.use_cases.notify_deal_stage_change import NotifyDealStageChangeUseCase
from src.interfaces.api.auth_dependencies import get_current_user
from src.application.dtos.auth_dtos import UserOutput
from src.interfaces.api.dependencies import (
    get_close_deal_use_case,
    get_convert_lead_use_case,
    get_list_deals_use_case,
    get_move_deal_stage_use_case,
    get_notify_deal_stage_change_use_case,
)
from src.interfaces.schemas.deal_schemas import CloseDealRequest, MoveDealStageRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deals", tags=["Сделки"])


@router.get(
    "",
    response_model=list[DealOutput],
    status_code=status.HTTP_200_OK,
    summary="Список сделок",
    description=(
        "Возвращает список сделок. "
        "Опциональная фильтрация: pipeline_id — по воронке, "
        "stage_id — по этапу, owner_id — по владельцу. "
        "Без фильтров — все сделки (административный режим)."
    ),
)
async def list_deals(
    pipeline_id: UUID | None = None,
    stage_id: UUID | None = None,
    owner_id: UUID | None = None,
    use_case: ListDealsUseCase = Depends(get_list_deals_use_case),
) -> list[DealOutput]:
    """GET /api/v1/deals — список сделок с опциональной фильтрацией."""
    data = ListDealsInput(pipeline_id=pipeline_id, stage_id=stage_id, owner_id=owner_id)
    return await use_case.execute(data)


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


@router.patch(
    "/{deal_id}/close",
    response_model=DealOutput,
    status_code=status.HTTP_200_OK,
    summary="Закрыть сделку (won / lost)",
    description=(
        "Закрывает открытую сделку как выигранную (won) или проигранную (lost). "
        "Записывает событие в журнал активностей. "
        "Уже закрытую сделку нельзя закрыть повторно (400)."
    ),
)
async def close_deal(
    deal_id: UUID,
    body: CloseDealRequest,
    use_case: CloseDealUseCase = Depends(get_close_deal_use_case),
    current_user: UserOutput = Depends(get_current_user),
) -> DealOutput:
    """PATCH /api/v1/deals/{deal_id}/close — закрытие сделки."""
    data = CloseDealInput(
        deal_id=deal_id,
        outcome=body.outcome,
        performed_by_id=current_user.id,
    )
    try:
        return await use_case.execute(data)
    except DealNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (DealAlreadyClosedError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


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
