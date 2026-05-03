"""
Юнит-тесты AddStageUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.pipeline_dtos import AddStageInput
from src.application.exceptions import PipelineNotFoundError
from src.application.use_cases.add_stage import AddStageUseCase
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(pipeline_repo) -> AddStageUseCase:
    return AddStageUseCase(pipeline_repo=pipeline_repo)


class TestAddStageNotFound:
    async def test_raises_when_pipeline_not_found(self, use_case, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(uuid4(), AddStageInput(name="New Stage"))


class TestAddStageOrder:
    async def test_order_is_zero_for_empty_pipeline(self, use_case, pipeline_repo):
        pipeline = Pipeline.create(name="Empty", owner_id=uuid4())
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(pipeline.id, AddStageInput(name="First Stage"))
        assert len(result.stages) == 1
        assert result.stages[0].order == 0

    async def test_order_is_max_plus_one_when_stages_exist(self, use_case, pipeline_repo):
        pipeline = Pipeline.create(name="Pipeline", owner_id=uuid4())
        stage = Stage.create(pipeline_id=pipeline.id, name="S1", order=2)
        pipeline.add_stage(stage)
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(pipeline.id, AddStageInput(name="S2"))
        orders = [s.order for s in result.stages]
        assert 3 in orders

    async def test_new_stage_has_correct_name(self, use_case, pipeline_repo):
        pipeline = Pipeline.create(name="Pipeline", owner_id=uuid4())
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(pipeline.id, AddStageInput(name="Negotiation", probability=0.7))
        new_stage = result.stages[0]
        assert new_stage.name == "Negotiation"
        assert new_stage.probability == 0.7
