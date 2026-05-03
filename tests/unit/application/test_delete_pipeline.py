"""
Юнит-тесты DeletePipelineUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.exceptions import PipelineNotFoundError
from src.application.use_cases.delete_pipeline import DeletePipelineUseCase
from src.domain.entities.pipeline import Pipeline


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(pipeline_repo) -> DeletePipelineUseCase:
    return DeletePipelineUseCase(pipeline_repo=pipeline_repo)


class TestDeletePipelineNotFound:
    async def test_raises_when_pipeline_not_found(self, use_case, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(uuid4())


class TestDeletePipelineSuccess:
    async def test_calls_delete_when_found(self, use_case, pipeline_repo):
        pipeline = Pipeline.create(name="To Delete", owner_id=uuid4())
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(pipeline.id)
        pipeline_repo.delete.assert_called_once_with(pipeline.id)
