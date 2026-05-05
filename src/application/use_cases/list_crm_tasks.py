from __future__ import annotations

from src.application.dtos.crm_task_dtos import ListTasksInput, TaskOutput
from src.domain.repositories.task_repository import ITaskRepository


class ListCrmTasksUseCase:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self._repo = task_repo

    async def execute(self, data: ListTasksInput) -> list[TaskOutput]:
        tasks = await self._repo.find_all(
            assignee_id=data.assignee_id,
            lead_id=data.lead_id,
            deal_id=data.deal_id,
            status=data.status,
            overdue_only=data.overdue_only,
        )
        return [TaskOutput.from_entity(t) for t in tasks]
