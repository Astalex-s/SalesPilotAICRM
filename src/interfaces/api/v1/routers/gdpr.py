"""
Роутер /api/v1/gdpr — операции GDPR: удаление данных, анонимизация, журнал аудита.
Тонкие контроллеры: вызвать use case → вернуть DTO.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from src.application.dtos.gdpr_dtos import (
    AnonymizeLeadOutput,
    DeleteUserDataOutput,
    GdprAuditLogOutput,
)
from src.application.use_cases.anonymize_lead import AnonymizeLeadUseCase
from src.application.use_cases.delete_user_data import DeleteUserDataUseCase
from src.application.use_cases.get_gdpr_audit_log import GetGdprAuditLogUseCase
from src.interfaces.api.dependencies import (
    get_anonymize_lead_use_case,
    get_delete_user_data_use_case,
    get_gdpr_audit_log_use_case,
)

router = APIRouter(prefix="/gdpr", tags=["GDPR"])


@router.post(
    "/users/{user_id}/delete",
    response_model=DeleteUserDataOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Удаление данных пользователя (GDPR Right to Erasure)",
    description=(
        "Физически удаляет все данные пользователя: лиды, сделки, email-сообщения "
        "и активности. Фиксирует событие в журнале аудита GDPR (Art. 17)."
    ),
)
async def delete_user_data(
    user_id: UUID,
    use_case: DeleteUserDataUseCase = Depends(get_delete_user_data_use_case),
) -> DeleteUserDataOutput:
    """POST /api/v1/gdpr/users/{user_id}/delete — Right to Erasure."""
    return await use_case.execute(user_id=user_id)


@router.post(
    "/leads/{lead_id}/anonymize",
    response_model=AnonymizeLeadOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Анонимизация лида (GDPR псевдонимизация)",
    description=(
        "Заменяет все PII-поля лида (имя, email, телефон, компания, заметки) "
        "на GDPR-безопасные заглушки. Удаляет email-сообщения и активности лида. "
        "Лид остаётся в системе для аналитики без персональных данных."
    ),
)
async def anonymize_lead(
    lead_id: UUID,
    use_case: AnonymizeLeadUseCase = Depends(get_anonymize_lead_use_case),
) -> AnonymizeLeadOutput:
    """POST /api/v1/gdpr/leads/{lead_id}/anonymize — псевдонимизация PII."""
    return await use_case.execute(lead_id=lead_id)


@router.get(
    "/audit-log",
    response_model=GdprAuditLogOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Журнал аудита GDPR",
    description=(
        "Возвращает записи журнала аудита GDPR с пагинацией "
        "(от новых к старым). Хранится не менее 3 лет (GDPR Art. 30)."
    ),
)
async def get_audit_log(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    use_case: GetGdprAuditLogUseCase = Depends(get_gdpr_audit_log_use_case),
) -> GdprAuditLogOutput:
    """GET /api/v1/gdpr/audit-log — журнал GDPR-событий."""
    return await use_case.execute(limit=limit, offset=offset)
