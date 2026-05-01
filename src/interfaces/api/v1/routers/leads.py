"""
Роутер /api/v1/leads.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import status as http_status

from src.application.dtos.activity_dtos import ActivityOutput
from src.application.dtos.lead_dtos import CreateLeadInput, GetLeadInput, LeadOutput, ListLeadsInput, UpdateLeadInput
from src.application.dtos.telegram_dtos import NotifyNewLeadInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.application.use_cases.get_lead import GetLeadUseCase
from src.application.use_cases.list_lead_activities import ListLeadActivitiesUseCase
from src.application.use_cases.list_leads import ListLeadsUseCase
from src.application.use_cases.notify_new_lead import NotifyNewLeadUseCase
from src.application.use_cases.update_lead import UpdateLeadUseCase
from src.domain.value_objects.enums import LeadStatus
from src.interfaces.api.dependencies import (
    get_create_lead_use_case,
    get_lead_use_case,
    get_list_lead_activities_use_case,
    get_list_leads_use_case,
    get_notify_new_lead_use_case,
    get_update_lead_use_case,
)
from src.interfaces.schemas.lead_schemas import UpdateLeadRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["Лиды"])


@router.post(
    "",
    response_model=LeadOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Создать лида",
    description="Создаёт нового лида. E-mail должен быть уникальным в системе.",
)
async def create_lead(
    body: CreateLeadInput,
    background_tasks: BackgroundTasks,
    use_case: CreateLeadUseCase = Depends(get_create_lead_use_case),
    notify_use_case: NotifyNewLeadUseCase = Depends(get_notify_new_lead_use_case),
) -> LeadOutput:
    """POST /api/v1/leads — создание нового лида."""
    result = await use_case.execute(body)

    # Фоновое уведомление — не блокирует ответ клиенту
    background_tasks.add_task(_send_new_lead_notification, notify_use_case, result)

    return result


@router.get(
    "",
    response_model=list[LeadOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Список лидов",
    description=(
        "Возвращает список лидов. "
        "Опциональная фильтрация: owner_id — по владельцу, status — по статусу. "
        "Без фильтров — все лиды (административный режим)."
    ),
)
async def list_leads(
    owner_id: UUID | None = None,
    lead_status: LeadStatus | None = None,
    use_case: ListLeadsUseCase = Depends(get_list_leads_use_case),
) -> list[LeadOutput]:
    """GET /api/v1/leads — список лидов с опциональной фильтрацией."""
    data = ListLeadsInput(owner_id=owner_id, status=lead_status)
    return await use_case.execute(data)


@router.patch(
    "/{lead_id}",
    response_model=LeadOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Обновить лида",
    description=(
        "Обновляет статус и/или заметки лида. "
        "Переходы статусов соответствуют машине состояний домена: "
        "new→contacted/qualified/unqualified, contacted→qualified/unqualified, "
        "qualified→unqualified, unqualified→qualified/contacted. "
        "Статусы CONVERTED и NEW нельзя установить напрямую."
    ),
)
async def update_lead(
    lead_id: UUID,
    body: UpdateLeadRequest,
    use_case: UpdateLeadUseCase = Depends(get_update_lead_use_case),
) -> LeadOutput:
    """PATCH /api/v1/leads/{lead_id} — обновление статуса/заметок лида."""
    data = UpdateLeadInput(lead_id=lead_id, status=body.status, notes=body.notes)
    return await use_case.execute(data)


@router.get(
    "/{lead_id}",
    response_model=LeadOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Получить лида по ID",
    description="Возвращает полные данные лида по его UUID.",
)
async def get_lead(
    lead_id: UUID,
    use_case: GetLeadUseCase = Depends(get_lead_use_case),
) -> LeadOutput:
    """GET /api/v1/leads/{lead_id} — получение одного лида."""
    return await use_case.execute(GetLeadInput(lead_id=lead_id))


@router.get(
    "/{lead_id}/activities",
    response_model=list[ActivityOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Журнал активностей лида",
    description="Возвращает все активности лида, упорядоченные от новых к старым.",
)
async def list_lead_activities(
    lead_id: UUID,
    use_case: ListLeadActivitiesUseCase = Depends(get_list_lead_activities_use_case),
) -> list[ActivityOutput]:
    """GET /api/v1/leads/{lead_id}/activities — журнал активностей."""
    return await use_case.execute(lead_id)


# ── Фоновые задачи ─────────────────────────────────────────────────────────────

async def _send_new_lead_notification(
    use_case: NotifyNewLeadUseCase,
    lead: LeadOutput,
) -> None:
    """Отправляет Telegram-уведомление о новом лиде в фоне.

    Ошибки конфигурации и транспорта не прерывают основной поток — только логируются.
    """
    try:
        data = NotifyNewLeadInput(
            lead_id=lead.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            company=lead.company,
            source=lead.source,
        )
        await use_case.execute(data)
    except TelegramNotConfiguredError:
        # Telegram не настроен — молча пропускаем
        pass
    except Exception:
        logger.exception("Ошибка отправки Telegram-уведомления о новом лиде %s", lead.id)
