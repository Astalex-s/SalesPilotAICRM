"""
Юнит-тесты DeleteStageUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.exceptions import PipelineNotFoundError
from src.application.use_cases.delete_stage import DeleteStageUseCase
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


def _make_pipeline_with_stage():
    pipeline = Pipeline.create(name="Pipeline", owner_id=uuid4())
    stage = Stage.create(pipeline_id=pipeline.id, name="Stage A", order=0)
    pipeline.add_stage(stage)
    return pipeline, stage


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(pipeline_repo) -> DeleteStageUseCase:
    return DeleteStageUseCase(pipeline_repo=pipeline_repo)


class TestDeleteStageNotFound:
    async def test_raises_when_pipeline_not_found(self, use_case, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(uuid4(), uuid4())


class TestDeleteStageSuccess:
    async def test_removes_stage_from_pipeline(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(pipeline.id, stage.id)
        assert all(s.id != stage.id for s in result.stages)

    async def test_calls_save(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(pipeline.id, stage.id)
        pipeline_repo.save.assert_called_once()
