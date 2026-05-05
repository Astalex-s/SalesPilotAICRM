from __future__ import annotations

from src.application.dtos.crm_task_dtos import TaskOutput, UpdateTaskInput
from src.application.exceptions import TaskNotFoundError
from src.domain.repositories.task_repository import ITaskRepository


class UpdateCrmTaskUseCase:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self._repo = task_repo

    async def execute(self, data: UpdateTaskInput) -> TaskOutput:
        task = await self._repo.get_by_id(data.task_id)
        if task is None:
            raise TaskNotFoundError(data.task_id)
        task.update(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            assignee_id=data.assignee_id,
            status=data.status,
        )
        saved = await self._repo.save(task)
        return TaskOutput.from_entity(saved)
