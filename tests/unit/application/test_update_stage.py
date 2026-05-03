"""
Юнит-тесты UpdateStageUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.pipeline_dtos import UpdateStageInput
from src.application.exceptions import PipelineNotFoundError, StageNotInPipelineError
from src.application.use_cases.update_stage import UpdateStageUseCase
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


def _make_pipeline_with_stage():
    pipeline = Pipeline.create(name="Sales Pipeline", owner_id=uuid4())
    stage = Stage.create(pipeline_id=pipeline.id, name="Discovery", order=0, probability=0.3)
    pipeline.add_stage(stage)
    return pipeline, stage


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(pipeline_repo) -> UpdateStageUseCase:
    return UpdateStageUseCase(pipeline_repo=pipeline_repo)


class TestUpdateStageNotFound:
    async def test_raises_when_pipeline_not_found(self, use_case, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(uuid4(), uuid4(), UpdateStageInput())

    async def test_raises_when_stage_not_in_pipeline(self, use_case, pipeline_repo):
        pipeline, _ = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        with pytest.raises(StageNotInPipelineError):
            await use_case.execute(pipeline.id, uuid4(), UpdateStageInput())


class TestUpdateStageName:
    async def test_updates_name(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(
            pipeline.id, stage.id, UpdateStageInput(name="New Name")
        )
        updated_stage = next(s for s in result.stages if s.id == stage.id)
        assert updated_stage.name == "New Name"

    async def test_no_name_change_when_none(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(pipeline.id, stage.id, UpdateStageInput(name=None))
        updated_stage = next(s for s in result.stages if s.id == stage.id)
        assert updated_stage.name == "Discovery"


class TestUpdateStageProbability:
    async def test_updates_probability(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(
            pipeline.id, stage.id, UpdateStageInput(probability=0.9)
        )
        updated_stage = next(s for s in result.stages if s.id == stage.id)
        assert updated_stage.probability == 0.9


class TestUpdateStageColor:
    async def test_sets_color(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(
            pipeline.id, stage.id, UpdateStageInput(color="#FF0000")
        )
        updated_stage = next(s for s in result.stages if s.id == stage.id)
        assert updated_stage.color == "#FF0000"

    async def test_clears_color_when_clear_color_true(self, use_case, pipeline_repo):
        pipeline, stage = _make_pipeline_with_stage()
        stage.color = "#FF0000"
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(
            pipeline.id, stage.id, UpdateStageInput(clear_color=True)
        )
        updated_stage = next(s for s in result.stages if s.id == stage.id)
        assert updated_stage.color is None
