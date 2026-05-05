"""
Роутер /api/v1/leads.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

import csv
import io
import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi import status as http_status

from src.application.dtos.activity_dtos import ActivityOutput, AddCommentInput
from src.application.dtos.lead_dtos import (
    BulkImportInput,
    BulkImportLeadRow,
    BulkImportResult,
    CreateLeadInput,
    GetLeadInput,
    LeadOutput,
    ListLeadsInput,
    UpdateLeadInput,
)
from src.application.dtos.telegram_dtos import NotifyNewLeadInput
from src.application.dtos.auth_dtos import UserOutput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.bulk_import_leads import BulkImportLeadsUseCase
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.application.use_cases.get_lead import GetLeadUseCase
from src.application.use_cases.add_comment import AddCommentUseCase
from src.application.use_cases.list_lead_activities import ListLeadActivitiesUseCase
from src.application.use_cases.list_leads import ListLeadsUseCase
from src.application.use_cases.notify_new_lead import NotifyNewLeadUseCase
from src.application.use_cases.list_lead_tags import ListLeadTagsUseCase
from src.application.use_cases.update_lead import UpdateLeadUseCase
from src.domain.value_objects.enums import LeadSource, LeadStatus
from src.infrastructure.notifications.notification_bus import bus
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_add_comment_use_case,
    get_bulk_import_leads_use_case,
    get_create_lead_use_case,
    get_lead_use_case,
    get_list_lead_activities_use_case,
    get_list_lead_tags_use_case,
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

    # Фоновые задачи — не блокируют ответ клиенту
    background_tasks.add_task(_send_new_lead_notification, notify_use_case, result)
    background_tasks.add_task(
        bus.publish,
        {
            "type": "lead",
            "title_key": "notifications.items.leadCreated.title",
            "msg_key": "notifications.items.leadCreated.msg",
            "params": {
                "name": result.full_name,
                "company": result.company or "—",
            },
            "link": f"/leads/{result.id}",
            "timestamp": result.created_at.isoformat(),
        },
    )

    return result


@router.get(
    "/tags",
    response_model=list[str],
    status_code=http_status.HTTP_200_OK,
    summary="Все уникальные теги лидов",
    description="Возвращает список всех уникальных тегов для автодополнения.",
)
async def list_lead_tags(
    use_case: ListLeadTagsUseCase = Depends(get_list_lead_tags_use_case),
) -> list[str]:
    """GET /api/v1/leads/tags — все уникальные теги."""
    return await use_case.execute()


@router.get(
    "",
    response_model=list[LeadOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Список лидов",
    description=(
        "Возвращает список лидов. "
        "Опциональная фильтрация: owner_id — по владельцу, status — по статусу, tag — по тегу. "
        "Без фильтров — все лиды (административный режим)."
    ),
)
async def list_leads(
    owner_id: UUID | None = None,
    lead_status: LeadStatus | None = None,
    tag: str | None = None,
    use_case: ListLeadsUseCase = Depends(get_list_leads_use_case),
) -> list[LeadOutput]:
    """GET /api/v1/leads — список лидов с опциональной фильтрацией."""
    data = ListLeadsInput(owner_id=owner_id, status=lead_status, tag=tag)
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
    data = UpdateLeadInput(
        lead_id=lead_id,
        status=body.status,
        notes=body.notes,
        tags=body.tags,
        category=body.category,
    )
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


@router.post(
    "/{lead_id}/comments",
    response_model=ActivityOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Добавить комментарий к лиду",
    description="Создаёт заметку (NOTE) в журнале активностей лида.",
)
async def add_lead_comment(
    lead_id: UUID,
    body: AddCommentInput,
    current_user: UserOutput = Depends(get_current_user),
    use_case: AddCommentUseCase = Depends(get_add_comment_use_case),
) -> ActivityOutput:
    """POST /api/v1/leads/{lead_id}/comments — добавление комментария."""
    return await use_case.execute(
        entity_type="lead",
        entity_id=lead_id,
        performed_by_id=current_user.id,
        body=body.body,
    )


@router.post(
    "/bulk-import",
    response_model=BulkImportResult,
    status_code=http_status.HTTP_200_OK,
    summary="Массовый импорт лидов из CSV",
    description=(
        "Принимает CSV-файл и создаёт лидов пакетно. "
        "Обязательные колонки: first_name, last_name, email. "
        "Опциональные: phone, company, source. "
        "Дубли по e-mail пропускаются (skipped), не являются ошибкой."
    ),
)
async def bulk_import_leads(
    file: UploadFile = File(..., description="CSV-файл с лидами"),
    use_case: BulkImportLeadsUseCase = Depends(get_bulk_import_leads_use_case),
    current_user: UserOutput = Depends(get_current_user),
) -> BulkImportResult:
    """POST /api/v1/leads/bulk-import — массовый импорт из CSV."""
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    rows: list[BulkImportLeadRow] = []

    for raw_row in reader:
        row = {k.strip().lower(): (v or "").strip() for k, v in raw_row.items() if k}
        source_val = row.get("source", "other")
        try:
            source = LeadSource(source_val)
        except ValueError:
            source = LeadSource.OTHER

        rows.append(
            BulkImportLeadRow(
                first_name=row.get("first_name", ""),
                last_name=row.get("last_name", ""),
                email=row.get("email", ""),
                phone=row.get("phone") or None,
                company=row.get("company") or None,
                source=source,
            )
        )

    return await use_case.execute(BulkImportInput(rows=rows, owner_id=current_user.id))


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
