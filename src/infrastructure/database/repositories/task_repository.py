"""
SqlTaskRepository — реализация ITaskRepository на SQLAlchemy 2.0 async.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task import Task
from src.domain.repositories.task_repository import ITaskRepository
from src.domain.value_objects.enums import TaskStatus
from src.infrastructure.database.models.task_model import TaskModel


class SqlTaskRepository(ITaskRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, task_id: UUID) -> Task | None:
        row = await self._session.get(TaskModel, task_id)
        return row.to_entity() if row else None

    async def save(self, task: Task) -> Task:
        orm = TaskModel.from_entity(task)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return merged.to_entity()

    async def delete(self, task_id: UUID) -> None:
        row = await self._session.get(TaskModel, task_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_all(
        self,
        assignee_id: UUID | None = None,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> list[Task]:
        stmt = select(TaskModel)
        if assignee_id is not None:
            stmt = stmt.where(TaskModel.assignee_id == assignee_id)
        if lead_id is not None:
            stmt = stmt.where(TaskModel.lead_id == lead_id)
        if deal_id is not None:
            stmt = stmt.where(TaskModel.deal_id == deal_id)
        if status is not None:
            stmt = stmt.where(TaskModel.status == status)
        if overdue_only:
            now = datetime.now(timezone.utc)
            stmt = stmt.where(
                TaskModel.due_date < now,
                TaskModel.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            )
        stmt = stmt.order_by(TaskModel.due_date.asc().nulls_last(), TaskModel.created_at.desc())
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
