from __future__ import annotations

from uuid import UUID

from src.application.exceptions import TaskNotFoundError
from src.domain.repositories.task_repository import ITaskRepository


class DeleteCrmTaskUseCase:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self._repo = task_repo

    async def execute(self, task_id: UUID) -> None:
        task = await self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        await self._repo.delete(task_id)
