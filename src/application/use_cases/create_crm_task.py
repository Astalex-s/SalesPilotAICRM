from __future__ import annotations

from uuid import UUID

from src.application.dtos.crm_task_dtos import CreateTaskInput, TaskOutput
from src.domain.entities.task import Task
from src.domain.repositories.task_repository import ITaskRepository


class CreateCrmTaskUseCase:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self._repo = task_repo

    async def execute(self, data: CreateTaskInput, created_by_id: UUID) -> TaskOutput:
        task = Task.create(
            title=data.title,
            created_by_id=created_by_id,
            assignee_id=data.assignee_id,
            lead_id=data.lead_id,
            deal_id=data.deal_id,
            description=data.description,
            due_date=data.due_date,
        )
        saved = await self._repo.save(task)
        return TaskOutput.from_entity(saved)
