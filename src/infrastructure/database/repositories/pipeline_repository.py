"""
SqlPipelineRepository — реализация IPipelineRepository на SQLAlchemy 2.0 async.
При сохранении воронки синхронизирует коллекцию Stage:
добавляет новые, обновляет существующие, удаляет убранные.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.pipeline import Pipeline
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.infrastructure.database.models.pipeline_model import PipelineModel
from src.infrastructure.database.models.stage_model import StageModel


class SqlPipelineRepository(IPipelineRepository):
    """Реализация IPipelineRepository через SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Pipeline | None:
        """Возвращает воронку со всеми этапами по UUID или None."""
        row = await self._session.get(PipelineModel, entity_id)
        return row.to_entity() if row is not None else None

    async def save(self, entity: Pipeline) -> Pipeline:
        """Выполняет upsert воронки и синхронизирует её этапы."""
        # Сохраняем воронку
        pipeline_orm = PipelineModel.from_entity(entity)
        merged_pipeline = await self._session.merge(pipeline_orm)

        # Определяем актуальный набор ID этапов из доменной сущности
        incoming_ids = {s.id for s in entity.stages}

        # Удаляем этапы, которых уже нет в доменной сущности
        stmt = select(StageModel).where(StageModel.pipeline_id == entity.id)
        existing_rows = await self._session.scalars(stmt)
        for stage_row in existing_rows.all():
            if stage_row.id not in incoming_ids:
                await self._session.delete(stage_row)

        # Upsert каждого этапа из доменной сущности
        for stage in entity.stages:
            stage_orm = StageModel.from_entity(stage)
            await self._session.merge(stage_orm)

        await self._session.flush()

        # Перечитываем relationship stages после flush
        await self._session.refresh(merged_pipeline, ["stages"])
        return merged_pipeline.to_entity()

    async def delete(self, entity_id: UUID) -> None:
        """Удаляет воронку (каскадно удаляются этапы)."""
        row = await self._session.get(PipelineModel, entity_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def find_active(self) -> list[Pipeline]:
        """Возвращает все активные воронки со своими этапами."""
        stmt = select(PipelineModel).where(PipelineModel.is_active.is_(True))
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]

    async def find_by_owner(self, owner_id: UUID) -> list[Pipeline]:
        """Возвращает все воронки указанного пользователя."""
        stmt = select(PipelineModel).where(PipelineModel.owner_id == owner_id)
        rows = await self._session.scalars(stmt)
        return [r.to_entity() for r in rows.all()]
