"""
Юнит-тесты use case GetPipelineUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.pipeline_dtos import GetPipelineInput, PipelineOutput
from src.application.exceptions import PipelineNotFoundError
from src.application.use_cases.get_pipeline import GetPipelineUseCase
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_pipeline(stage_count: int = 2) -> Pipeline:
    """Создаёт тестовую воронку с заданным количеством этапов."""
    owner_id = uuid4()
    pipeline = Pipeline(
        id=uuid4(),
        name="Test Pipeline",
        owner_id=owner_id,
        stages=[],
    )
    for i in range(stage_count):
        stage = Stage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name=f"Stage {i + 1}",
            order=i,
            probability=0.5,
        )
        pipeline.add_stage(stage)
    return pipeline


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def pipeline_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    return repo


@pytest.fixture
def use_case(pipeline_repo: AsyncMock) -> GetPipelineUseCase:
    return GetPipelineUseCase(pipeline_repo=pipeline_repo)


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestGetPipelineHappyPath:
    async def test_returns_pipeline_output(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """execute возвращает PipelineOutput для существующей воронки."""
        pipeline = make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        assert isinstance(result, PipelineOutput)

    async def test_output_id_matches(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """ID воронки в DTO совпадает с ID сущности."""
        pipeline = make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        assert result.id == pipeline.id

    async def test_output_name_matches(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """Имя воронки в DTO совпадает."""
        pipeline = make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        assert result.name == "Test Pipeline"

    async def test_output_contains_stages(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """DTO содержит список этапов воронки."""
        pipeline = make_pipeline(stage_count=3)
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        assert len(result.stages) == 3

    async def test_stage_names_preserved(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """Имена этапов в DTO совпадают с именами в сущности."""
        pipeline = make_pipeline(stage_count=2)
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        stage_names = {s.name for s in result.stages}
        assert "Stage 1" in stage_names
        assert "Stage 2" in stage_names

    async def test_repo_get_by_id_called_with_correct_id(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """Репозиторий вызывается с правильным ID."""
        pipeline = make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(GetPipelineInput(pipeline_id=pipeline.id))
        pipeline_repo.get_by_id.assert_called_once_with(pipeline.id)


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestGetPipelineGuards:
    async def test_not_found_raises(
        self, use_case: GetPipelineUseCase, pipeline_repo: AsyncMock
    ) -> None:
        """Несуществующая воронка вызывает PipelineNotFoundError."""
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(GetPipelineInput(pipeline_id=uuid4()))
