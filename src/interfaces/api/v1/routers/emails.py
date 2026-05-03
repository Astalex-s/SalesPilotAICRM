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
    EmailSyncOutput,
    EmailThreadDetail,
    EmailThreadSummary,
    FetchEmailsInput,
    LinkEmailToLeadInput,
    ListStoredEmailsInput,
    SendEmailInput,
)
from src.application.use_cases.fetch_emails import FetchEmailsUseCase
from src.application.use_cases.get_email_thread import GetEmailThreadUseCase
from src.application.use_cases.link_email_to_lead import LinkEmailToLeadUseCase
from src.application.use_cases.list_email_threads import ListEmailThreadsUseCase
from src.application.use_cases.list_stored_emails import ListStoredEmailsUseCase
from src.application.use_cases.send_email import SendEmailUseCase
from src.application.use_cases.trigger_email_sync import TriggerEmailSyncUseCase
from src.interfaces.api.dependencies import (
    get_email_thread_use_case,
    get_fetch_emails_use_case,
    get_link_email_to_lead_use_case,
    get_list_email_threads_use_case,
    get_list_stored_emails_use_case,
    get_send_email_use_case,
    get_trigger_email_sync_use_case,
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


@router.get(
    "/stored",
    response_model=list[EmailMessageOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Список писем из БД",
    description=(
        "Возвращает письма из локальной БД без вызова Gmail API. "
        "Подходит для быстрой загрузки инбокса при открытии страницы."
    ),
)
async def list_stored_emails(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    use_case: ListStoredEmailsUseCase = Depends(get_list_stored_emails_use_case),
) -> list[EmailMessageOutput]:
    """GET /api/v1/emails/stored — письма из БД без Gmail API."""
    return await use_case.execute(ListStoredEmailsInput(limit=limit, offset=offset))


@router.post(
    "/sync",
    response_model=EmailSyncOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="Запустить синхронизацию Gmail в фоне",
    description=(
        "Ставит задачу синхронизации писем из Gmail в очередь Celery. "
        "Возвращает task_id немедленно; выполнение происходит асинхронно."
    ),
)
async def trigger_email_sync(
    query: str = Query(default="", description="Строка поиска Gmail"),
    max_results: int = Query(default=100, ge=1, le=500),
    use_case: TriggerEmailSyncUseCase = Depends(get_trigger_email_sync_use_case),
) -> EmailSyncOutput:
    """POST /api/v1/emails/sync — поставить синхронизацию в Celery очередь."""
    return await use_case.execute(query=query, max_results=max_results)


@router.get(
    "/threads",
    response_model=list[EmailThreadSummary],
    status_code=http_status.HTTP_200_OK,
    summary="Список тредов (цепочек писем)",
    description=(
        "Группирует сохранённые письма по gmail_thread_id. "
        "Каждый тред содержит тему, количество писем, дату последнего и список участников."
    ),
)
async def list_email_threads(
    use_case: ListEmailThreadsUseCase = Depends(get_list_email_threads_use_case),
) -> list[EmailThreadSummary]:
    """GET /api/v1/emails/threads — список тредов."""
    return await use_case.execute()


@router.get(
    "/threads/{thread_id}",
    response_model=EmailThreadDetail,
    status_code=http_status.HTTP_200_OK,
    summary="Все письма треда",
    description=(
        "Возвращает все письма конкретного треда (по gmail_thread_id) "
        "в хронологическом порядке от первого к последнему."
    ),
)
async def get_email_thread(
    thread_id: str,
    use_case: GetEmailThreadUseCase = Depends(get_email_thread_use_case),
) -> EmailThreadDetail:
    """GET /api/v1/emails/threads/{thread_id} — полный тред."""
    return await use_case.execute(thread_id)


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
