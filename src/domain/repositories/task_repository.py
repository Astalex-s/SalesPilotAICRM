"""
ITaskRepository — интерфейс репозитория для CRM-задач.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.task import Task
from src.domain.value_objects.enums import TaskStatus


class ITaskRepository(ABC):

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None: ...

    @abstractmethod
    async def save(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: UUID) -> None: ...

    @abstractmethod
    async def find_all(
        self,
        assignee_id: UUID | None = None,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> list[Task]: ...
