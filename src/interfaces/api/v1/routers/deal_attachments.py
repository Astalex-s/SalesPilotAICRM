"""
Роутер /api/v1/deals/{deal_id}/attachments — управление вложениями сделки.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from src.application.dtos.auth_dtos import UserOutput
from src.application.dtos.deal_attachment_dtos import DealAttachmentOutput
from src.application.exceptions import DealNotFoundError
from src.application.use_cases.delete_deal_attachment import DeleteDealAttachmentUseCase
from src.application.use_cases.list_deal_attachments import ListDealAttachmentsUseCase
from src.application.use_cases.upload_deal_attachment import UploadDealAttachmentUseCase
from src.domain.repositories.deal_attachment_repository import IDealAttachmentRepository
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_attachment_repo,
    get_delete_attachment_use_case,
    get_list_attachments_use_case,
    get_upload_attachment_use_case,
)

router = APIRouter(prefix="/deals", tags=["Вложения сделок"])


@router.post(
    "/{deal_id}/attachments",
    response_model=DealAttachmentOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить файл к сделке",
)
async def upload_attachment(
    deal_id: UUID,
    file: UploadFile = File(...),
    use_case: UploadDealAttachmentUseCase = Depends(get_upload_attachment_use_case),
    current_user: UserOutput = Depends(get_current_user),
) -> DealAttachmentOutput:
    file_data = await file.read()
    try:
        return await use_case.execute(
            deal_id=deal_id,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            file_data=file_data,
            uploaded_by_id=current_user.id,
        )
    except DealNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{deal_id}/attachments",
    response_model=list[DealAttachmentOutput],
    status_code=status.HTTP_200_OK,
    summary="Список вложений сделки",
)
async def list_attachments(
    deal_id: UUID,
    use_case: ListDealAttachmentsUseCase = Depends(get_list_attachments_use_case),
    _: UserOutput = Depends(get_current_user),
) -> list[DealAttachmentOutput]:
    return await use_case.execute(deal_id)


@router.delete(
    "/{deal_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Удалить вложение",
)
async def delete_attachment(
    deal_id: UUID,
    attachment_id: UUID,
    use_case: DeleteDealAttachmentUseCase = Depends(get_delete_attachment_use_case),
    _: UserOutput = Depends(get_current_user),
) -> None:
    await use_case.execute(attachment_id)


@router.get(
    "/{deal_id}/attachments/{attachment_id}/download",
    summary="Скачать вложение",
    response_class=FileResponse,
)
async def download_attachment(
    deal_id: UUID,
    attachment_id: UUID,
    repo: IDealAttachmentRepository = Depends(get_attachment_repo),
    _: UserOutput = Depends(get_current_user),
) -> FileResponse:
    att = await repo.get_by_id(attachment_id)
    if att is None or att.deal_id != deal_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вложение не найдено.")
    return FileResponse(
        path=att.storage_path,
        filename=att.filename,
        media_type=att.content_type,
    )
