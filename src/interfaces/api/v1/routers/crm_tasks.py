"""
Роутер /api/v1/tasks — CRM-задачи (to-do, назначение на менеджера, дедлайн).
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.crm_task_dtos import (
    CreateTaskInput,
    ListTasksInput,
    TaskOutput,
    UpdateTaskInput,
)
from src.application.dtos.auth_dtos import UserOutput
from src.application.use_cases.create_crm_task import CreateCrmTaskUseCase
from src.application.use_cases.delete_crm_task import DeleteCrmTaskUseCase
from src.application.use_cases.list_crm_tasks import ListCrmTasksUseCase
from src.application.use_cases.update_crm_task import UpdateCrmTaskUseCase
from src.domain.value_objects.enums import TaskStatus
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_create_crm_task_use_case,
    get_delete_crm_task_use_case,
    get_list_crm_tasks_use_case,
    get_update_crm_task_use_case,
)

router = APIRouter(prefix="/tasks", tags=["CRM Задачи"])


@router.post(
    "",
    response_model=TaskOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Создать задачу",
)
async def create_task(
    body: CreateTaskInput,
    current_user: UserOutput = Depends(get_current_user),
    use_case: CreateCrmTaskUseCase = Depends(get_create_crm_task_use_case),
) -> TaskOutput:
    return await use_case.execute(body, created_by_id=current_user.id)


@router.get(
    "",
    response_model=list[TaskOutput],
    status_code=http_status.HTTP_200_OK,
    summary="Список задач",
)
async def list_tasks(
    assignee_id: UUID | None = None,
    lead_id: UUID | None = None,
    deal_id: UUID | None = None,
    status: TaskStatus | None = None,
    overdue_only: bool = False,
    use_case: ListCrmTasksUseCase = Depends(get_list_crm_tasks_use_case),
) -> list[TaskOutput]:
    data = ListTasksInput(
        assignee_id=assignee_id,
        lead_id=lead_id,
        deal_id=deal_id,
        status=status,
        overdue_only=overdue_only,
    )
    return await use_case.execute(data)


@router.patch(
    "/{task_id}",
    response_model=TaskOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Обновить задачу",
)
async def update_task(
    task_id: UUID,
    body: UpdateTaskInput,
    use_case: UpdateCrmTaskUseCase = Depends(get_update_crm_task_use_case),
) -> TaskOutput:
    data = UpdateTaskInput(
        task_id=task_id,
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        assignee_id=body.assignee_id,
        status=body.status,
    )
    return await use_case.execute(data)


@router.delete(
    "/{task_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу",
)
async def delete_task(
    task_id: UUID,
    use_case: DeleteCrmTaskUseCase = Depends(get_delete_crm_task_use_case),
) -> None:
    await use_case.execute(task_id)
