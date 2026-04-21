"""
Роутер /api/v1/leads.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.lead_dtos import CreateLeadInput, LeadOutput, ListLeadsInput
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.application.use_cases.list_leads import ListLeadsUseCase
from src.domain.value_objects.enums import LeadStatus
from src.interfaces.api.dependencies import (
    get_create_lead_use_case,
    get_list_leads_use_case,
)

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
    use_case: CreateLeadUseCase = Depends(get_create_lead_use_case),
) -> LeadOutput:
    """POST /api/v1/leads — создание нового лида."""
    return await use_case.execute(body)


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
