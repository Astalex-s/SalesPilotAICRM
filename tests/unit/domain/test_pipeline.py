"""
Юнит-тесты доменных сущностей Pipeline и Stage.
"""
import pytest
from uuid import uuid4

from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.exceptions import PipelineStageOrderError, StageNotFoundError


@pytest.fixture
def pipeline():
    return Pipeline.create(name="Sales Pipeline", owner_id=uuid4())


@pytest.fixture
def make_stage(pipeline):
    def _make(name: str, order: int, probability: float = 0.5) -> Stage:
        return Stage.create(
            pipeline_id=pipeline.id,
            name=name,
            order=order,
            probability=probability,
        )
    return _make


class TestPipeline:
    def test_create_pipeline(self, pipeline: Pipeline) -> None:
        assert pipeline.name == "Sales Pipeline"
        assert pipeline.is_active
        assert pipeline.stage_count == 0

    def test_add_stage_increases_count(self, pipeline, make_stage) -> None:
        pipeline.add_stage(make_stage("Prospecting", 1))
        assert pipeline.stage_count == 1

    def test_stages_sorted_by_order(self, pipeline, make_stage) -> None:
        pipeline.add_stage(make_stage("Closing", 3))
        pipeline.add_stage(make_stage("Negotiation", 2))
        pipeline.add_stage(make_stage("Prospecting", 1))
        orders = [s.order for s in pipeline.stages]
        assert orders == [1, 2, 3]

    def test_duplicate_order_raises(self, pipeline, make_stage) -> None:
        pipeline.add_stage(make_stage("Prospecting", 1))
        with pytest.raises(PipelineStageOrderError):
            pipeline.add_stage(make_stage("Duplicate", 1))

    def test_stage_wrong_pipeline_raises(self, pipeline) -> None:
        # Этап принадлежит другой воронке
        foreign_stage = Stage.create(
            pipeline_id=uuid4(),
            name="Foreign",
            order=1,
        )
        with pytest.raises(PipelineStageOrderError):
            pipeline.add_stage(foreign_stage)

    def test_first_and_last_stage(self, pipeline, make_stage) -> None:
        pipeline.add_stage(make_stage("First", 1))
        pipeline.add_stage(make_stage("Last", 5))
        assert pipeline.first_stage.name == "First"
        assert pipeline.last_stage.name == "Last"

    def test_remove_stage(self, pipeline, make_stage) -> None:
        s = make_stage("Removable", 1)
        pipeline.add_stage(s)
        pipeline.remove_stage(s.id)
        assert pipeline.stage_count == 0

    def test_remove_nonexistent_stage_raises(self, pipeline) -> None:
        with pytest.raises(StageNotFoundError):
            pipeline.remove_stage(uuid4())

    def test_has_stage(self, pipeline, make_stage) -> None:
        s = make_stage("Check", 1)
        pipeline.add_stage(s)
        assert pipeline.has_stage(s.id)
        assert not pipeline.has_stage(uuid4())

    def test_empty_pipeline_first_last_none(self, pipeline) -> None:
        assert pipeline.first_stage is None
        assert pipeline.last_stage is None


class TestStage:
    def test_invalid_probability_raises(self) -> None:
        with pytest.raises(ValueError, match="probability"):
            Stage.create(pipeline_id=uuid4(), name="Bad", order=1, probability=1.5)

    def test_negative_order_raises(self) -> None:
        with pytest.raises(ValueError, match="order"):
            Stage.create(pipeline_id=uuid4(), name="Bad", order=-1)

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Stage.create(pipeline_id=uuid4(), name="", order=1)
