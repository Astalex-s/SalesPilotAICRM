"""
SqlActivityRepository — реализация IActivityRepository на SQLAlchemy 2.0 async.
Append-only: метод delete() защищён NotImplementedError — журнал аудита иммутабелен.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.activity import Activity, EntityType
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.value_objects.enums import ActivityType
from src.infrastructure.database.models.activity_model import ActivityModel


class SqlActivityRepository(IActivityRepository):
    """Реализация IActivityRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Activity | None:
        """Возвращает активность по UUID или None."""
        row = await self._session.get(ActivityModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: Activity) -> Activity:
        """Добавляет новую активность в append-only журнал."""
        orm = ActivityModel.from_entity(entity)
        self._session.add(orm)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> None:
        """Удаление запрещено — активности являются иммутабельным журналом аудита."""
        raise NotImplementedError(
            "Активности являются append-only журналом аудита — удаление запрещено."
        )

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Activity]:
        """Возвращает все активности сущности, отсортированные от новых к старым."""
        stmt = (
            select(ActivityModel)
            .where(
                ActivityModel.entity_type == entity_type,
                ActivityModel.entity_id == entity_id,
            )
            .order_by(ActivityModel.occurred_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_type(self, activity_type: ActivityType) -> list[Activity]:
        """Возвращает все активности указанного типа."""
        stmt = select(ActivityModel).where(
            ActivityModel.activity_type == activity_type
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_performer(self, user_id: UUID) -> list[Activity]:
        """Возвращает все активности исполнителя, отсортированные от новых к старым."""
        stmt = (
            select(ActivityModel)
            .where(ActivityModel.performed_by_id == user_id)
            .order_by(ActivityModel.occurred_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
