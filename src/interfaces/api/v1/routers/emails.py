"""
Роутер /api/v1/emails — операции с Gmail-письмами в CRM.
Тонкие контроллеры: принять запрос → use case → DTO.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from src.application.dtos.email_message_dtos import (
    EmailMessageOutput,
    FetchEmailsInput,
    LinkEmailToLeadInput,
    SendEmailInput,
)
from src.application.use_cases.fetch_emails import FetchEmailsUseCase
from src.application.use_cases.link_email_to_lead import LinkEmailToLeadUseCase
from src.application.use_cases.send_email import SendEmailUseCase
from src.interfaces.api.dependencies import (
    get_fetch_emails_use_case,
    get_link_email_to_lead_use_case,
    get_send_email_use_case,
)

router = APIRouter(prefix="/emails", tags=["Email-интеграция"])


@router.post(
    "/send",
    response_model=EmailMessageOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Отправить письмо через Gmail",
    description=(
        "Отправляет письмо через авторизованный Gmail-аккаунт. "
        "Опционально привязывает письмо к лиду и создаёт запись активности."
    ),
)
async def send_email(
    data: SendEmailInput,
    use_case: SendEmailUseCase = Depends(get_send_email_use_case),
) -> EmailMessageOutput:
    """POST /api/v1/emails/send — отправить письмо."""
    return await use_case.execute(data)


@router.get(
    "",
    response_model=list[EmailMessageOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Загрузить письма из Gmail",
    description=(
        "Загружает письма из Gmail-ящика и сохраняет новые в CRM. "
        "Поддерживает строку поиска Gmail (например, 'from:client@corp.com'). "
        "Уже сохранённые письма пропускаются. "
        "Возвращает только новые письма, загруженные в этот раз."
    ),
)
async def fetch_emails(
    query: str = Query(default="", description="Строка поиска Gmail"),
    max_results: int = Query(default=50, ge=1, le=500),
    use_case: FetchEmailsUseCase = Depends(get_fetch_emails_use_case),
) -> list[EmailMessageOutput]:
    """GET /api/v1/emails — загрузить письма из Gmail."""
    return await use_case.execute(
        FetchEmailsInput(query=query, max_results=max_results)
    )


@router.post(
    "/{email_message_id}/link-lead",
    response_model=EmailMessageOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Привязать письмо к лиду",
    description=(
        "Устанавливает связь между сохранённым письмом и лидом. "
        "Позволяет вручную дополнить автопривязку или исправить её."
    ),
)
async def link_email_to_lead(
    email_message_id: UUID,
    lead_id: UUID = Query(..., description="ID лида для привязки"),
    use_case: LinkEmailToLeadUseCase = Depends(get_link_email_to_lead_use_case),
) -> EmailMessageOutput:
    """POST /api/v1/emails/{id}/link-lead — привязать письмо к лиду."""
    return await use_case.execute(
        LinkEmailToLeadInput(
            email_message_id=email_message_id,
            lead_id=lead_id,
        )
    )
