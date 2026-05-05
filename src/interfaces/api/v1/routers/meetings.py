"""
Роутер /api/v1/meetings — CRM-встречи/события (календарь).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.meeting_dtos import (
    CreateMeetingInput,
    ListMeetingsInput,
    MeetingOutput,
    UpdateMeetingInput,
)
from src.application.dtos.auth_dtos import UserOutput
from src.application.use_cases.create_meeting import CreateMeetingUseCase
from src.application.use_cases.delete_meeting import DeleteMeetingUseCase
from src.application.use_cases.list_meetings import ListMeetingsUseCase
from src.application.use_cases.update_meeting import UpdateMeetingUseCase
from src.domain.value_objects.enums import MeetingStatus
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_create_meeting_use_case,
    get_delete_meeting_use_case,
    get_list_meetings_use_case,
    get_update_meeting_use_case,
)

router = APIRouter(prefix="/meetings", tags=["Встречи / Календарь"])


@router.post(
    "",
    response_model=MeetingOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Создать встречу",
)
async def create_meeting(
    body: CreateMeetingInput,
    current_user: UserOutput = Depends(get_current_user),
    use_case: CreateMeetingUseCase = Depends(get_create_meeting_use_case),
) -> MeetingOutput:
    return await use_case.execute(body, created_by_id=current_user.id)


@router.get(
    "",
    response_model=list[MeetingOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Список встреч",
)
async def list_meetings(
    lead_id: UUID | None = None,
    deal_id: UUID | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    status: MeetingStatus | None = None,
    use_case: ListMeetingsUseCase = Depends(get_list_meetings_use_case),
) -> list[MeetingOutput]:
    data = ListMeetingsInput(
        lead_id=lead_id,
        deal_id=deal_id,
        from_date=from_date,
        to_date=to_date,
        status=status,
    )
    return await use_case.execute(data)


@router.patch(
    "/{meeting_id}",
    response_model=MeetingOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Обновить встречу",
)
async def update_meeting(
    meeting_id: UUID,
    body: UpdateMeetingInput,
    use_case: UpdateMeetingUseCase = Depends(get_update_meeting_use_case),
) -> MeetingOutput:
    data = UpdateMeetingInput(
        meeting_id=meeting_id,
        title=body.title,
        description=body.description,
        start_time=body.start_time,
        end_time=body.end_time,
        location=body.location,
        status=body.status,
    )
    return await use_case.execute(data)


@router.delete(
    "/{meeting_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Удалить встречу",
)
async def delete_meeting(
    meeting_id: UUID,
    use_case: DeleteMeetingUseCase = Depends(get_delete_meeting_use_case),
) -> None:
    await use_case.execute(meeting_id)
