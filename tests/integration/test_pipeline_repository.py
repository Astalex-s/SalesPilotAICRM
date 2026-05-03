"""
Интеграционные тесты SqlPipelineRepository (SQLite in-memory).
"""
from __future__ import annotations

import pytest
from uuid import uuid4

from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.infrastructure.database.repositories.pipeline_repository import SqlPipelineRepository


def _make_pipeline(owner_id=None) -> Pipeline:
    return Pipeline.create(name="Test Pipeline", owner_id=owner_id or uuid4())


def _make_stage(pipeline_id, order=0, name="Stage A") -> Stage:
    return Stage.create(pipeline_id=pipeline_id, name=name, order=order, probability=0.5)


@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    repo = SqlPipelineRepository(db_session)
    pipeline = _make_pipeline()
    stage = _make_stage(pipeline.id)
    pipeline.add_stage(stage)

    saved = await repo.save(pipeline)
    assert saved.id == pipeline.id
    assert len(saved.stages) == 1

    found = await repo.get_by_id(pipeline.id)
    assert found is not None
    assert found.name == "Test Pipeline"
    assert len(found.stages) == 1


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(db_session):
    repo = SqlPipelineRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_save_updates_stages(db_session):
    repo = SqlPipelineRepository(db_session)
    pipeline = _make_pipeline()
    stage1 = _make_stage(pipeline.id, order=0, name="S1")
    pipeline.add_stage(stage1)
    await repo.save(pipeline)

    stage2 = _make_stage(pipeline.id, order=1, name="S2")
    pipeline.add_stage(stage2)
    saved = await repo.save(pipeline)
    assert len(saved.stages) == 2


@pytest.mark.asyncio
async def test_save_removes_deleted_stage(db_session):
    repo = SqlPipelineRepository(db_session)
    pipeline = _make_pipeline()
    stage1 = _make_stage(pipeline.id, order=0, name="Keep")
    stage2 = _make_stage(pipeline.id, order=1, name="Remove")
    pipeline.add_stage(stage1)
    pipeline.add_stage(stage2)
    await repo.save(pipeline)

    pipeline.remove_stage(stage2.id)
    saved = await repo.save(pipeline)
    assert len(saved.stages) == 1
    assert saved.stages[0].name == "Keep"


@pytest.mark.asyncio
async def test_delete(db_session):
    repo = SqlPipelineRepository(db_session)
    pipeline = _make_pipeline()
    await repo.save(pipeline)

    await repo.delete(pipeline.id)
    found = await repo.get_by_id(pipeline.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(db_session):
    repo = SqlPipelineRepository(db_session)
    await repo.delete(uuid4())  # should not raise


@pytest.mark.asyncio
async def test_find_active(db_session):
    repo = SqlPipelineRepository(db_session)
    pipeline = _make_pipeline()
    await repo.save(pipeline)

    active = await repo.find_active()
    assert any(p.id == pipeline.id for p in active)


@pytest.mark.asyncio
async def test_find_active_excludes_inactive(db_session):
    from src.infrastructure.database.models.pipeline_model import PipelineModel
    from datetime import datetime, timezone

    repo = SqlPipelineRepository(db_session)
    inactive = PipelineModel(
        id=uuid4(),
        name="Inactive",
        owner_id=uuid4(),
        is_active=False,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(inactive)
    await db_session.flush()

    active = await repo.find_active()
    assert all(p.is_active for p in active)


@pytest.mark.asyncio
async def test_find_by_owner(db_session):
    repo = SqlPipelineRepository(db_session)
    owner_id = uuid4()
    pipeline = Pipeline.create(name="Owner Pipeline", owner_id=owner_id)
    await repo.save(pipeline)

    results = await repo.find_by_owner(owner_id)
    assert any(p.id == pipeline.id for p in results)


@pytest.mark.asyncio
async def test_find_by_owner_returns_empty_for_unknown(db_session):
    repo = SqlPipelineRepository(db_session)
    results = await repo.find_by_owner(uuid4())
    assert results == []
