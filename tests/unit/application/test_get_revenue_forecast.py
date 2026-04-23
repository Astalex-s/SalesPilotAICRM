"""
Юнит-тесты GetRevenueForecastUseCase.
Проверяют: взвешенный прогноз, группировку по воронкам/этапам, сортировку.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.get_revenue_forecast import GetRevenueForecastUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.value_objects.money import Money


@pytest.fixture
def deal_repo():
    return AsyncMock()


@pytest.fixture
def pipeline_repo():
    return AsyncMock()


@pytest.fixture
def use_case(deal_repo, pipeline_repo):
    return GetRevenueForecastUseCase(deal_repo, pipeline_repo)


@pytest.fixture
def owner_id():
    return uuid4()


def make_pipeline_with_stage(owner_id, stage_name="Q1", stage_order=1, probability=0.5):
    """Создаёт воронку с одним этапом."""
    pipeline = Pipeline.create("Test Pipeline", owner_id)
    stage = Stage.create(pipeline.id, stage_name, stage_order, probability)
    pipeline.add_stage(stage)
    return pipeline, stage


class TestGetRevenueForecastEmpty:
    async def test_empty_returns_zeros(self, use_case, deal_repo, pipeline_repo) -> None:
        deal_repo.find_all.return_value = []
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.closed_revenue == 0.0
        assert result.pipeline_value == 0.0
        assert result.weighted_forecast == 0.0
        assert result.by_pipeline == []
        assert result.by_stage == []


class TestGetRevenueForecastCalculations:
    async def test_closed_revenue_from_won_deals(
        self, use_case, deal_repo, pipeline_repo, owner_id
    ) -> None:
        pipeline, stage = make_pipeline_with_stage(owner_id, probability=0.8)
        pipeline_repo.find_active.return_value = [pipeline]

        d1 = Deal.create("Won Deal", owner_id, stage.id, pipeline.id, Money(Decimal("1000")))
        d1.win()
        deal_repo.find_all.return_value = [d1]

        result = await use_case.execute()

        assert result.closed_revenue == 1000.0
        assert result.pipeline_value == 0.0  # нет OPEN сделок
        assert result.weighted_forecast == 0.0

    async def test_weighted_forecast_calculation(
        self, use_case, deal_repo, pipeline_repo, owner_id
    ) -> None:
        pipeline, stage = make_pipeline_with_stage(owner_id, probability=0.4)
        pipeline_repo.find_active.return_value = [pipeline]

        d1 = Deal.create("Open Deal", owner_id, stage.id, pipeline.id, Money(Decimal("500")))
        d2 = Deal.create("Open Deal 2", owner_id, stage.id, pipeline.id, Money(Decimal("500")))
        deal_repo.find_all.return_value = [d1, d2]

        result = await use_case.execute()

        assert result.pipeline_value == 1000.0
        assert result.weighted_forecast == 400.0  # 1000 * 0.4

    async def test_by_stage_entry(self, use_case, deal_repo, pipeline_repo, owner_id) -> None:
        pipeline, stage = make_pipeline_with_stage(owner_id, "Prospect", 1, 0.3)
        pipeline_repo.find_active.return_value = [pipeline]

        deal = Deal.create("D", owner_id, stage.id, pipeline.id, Money(Decimal("2000")))
        deal_repo.find_all.return_value = [deal]

        result = await use_case.execute()

        assert len(result.by_stage) == 1
        entry = result.by_stage[0]
        assert entry.stage_id == stage.id
        assert entry.stage_name == "Prospect"
        assert entry.pipeline_id == pipeline.id
        assert entry.probability == 0.3
        assert entry.deal_count == 1
        assert entry.total_value == 2000.0
        assert entry.weighted_forecast == 600.0  # 2000 * 0.3

    async def test_by_pipeline_entry(self, use_case, deal_repo, pipeline_repo, owner_id) -> None:
        pipeline, stage = make_pipeline_with_stage(owner_id, probability=0.5)
        pipeline_repo.find_active.return_value = [pipeline]

        open_deal = Deal.create("Open", owner_id, stage.id, pipeline.id, Money(Decimal("800")))
        won_deal = Deal.create("Won", owner_id, stage.id, pipeline.id, Money(Decimal("200")))
        won_deal.win()
        deal_repo.find_all.return_value = [open_deal, won_deal]

        result = await use_case.execute()

        assert len(result.by_pipeline) == 1
        p_entry = result.by_pipeline[0]
        assert p_entry.pipeline_id == pipeline.id
        assert p_entry.open_deals == 1
        assert p_entry.pipeline_value == 800.0
        assert p_entry.closed_revenue == 200.0
        assert p_entry.weighted_forecast == 400.0  # 800 * 0.5

    async def test_by_stage_sorted_descending(
        self, use_case, deal_repo, pipeline_repo, owner_id
    ) -> None:
        """Этапы сортируются по убыванию weighted_forecast."""
        pipeline = Pipeline.create("Pipeline", owner_id)
        stage_low = Stage.create(pipeline.id, "Low", 1, 0.1)
        stage_high = Stage.create(pipeline.id, "High", 2, 0.9)
        pipeline.add_stage(stage_low)
        pipeline.add_stage(stage_high)
        pipeline_repo.find_active.return_value = [pipeline]

        d_low = Deal.create("D-low", owner_id, stage_low.id, pipeline.id, Money(Decimal("100")))
        d_high = Deal.create("D-high", owner_id, stage_high.id, pipeline.id, Money(Decimal("100")))
        deal_repo.find_all.return_value = [d_low, d_high]

        result = await use_case.execute()

        assert result.by_stage[0].stage_name == "High"
        assert result.by_stage[1].stage_name == "Low"

    async def test_orphan_stage_id_skipped(
        self, use_case, deal_repo, pipeline_repo, owner_id
    ) -> None:
        """Сделка с stage_id несуществующего этапа не включается в прогноз."""
        pipeline, stage = make_pipeline_with_stage(owner_id)
        pipeline_repo.find_active.return_value = [pipeline]

        orphan_stage_id = uuid4()
        deal = Deal.create("Orphan", owner_id, orphan_stage_id, pipeline.id, Money(Decimal("999")))
        deal_repo.find_all.return_value = [deal]

        result = await use_case.execute()

        assert result.weighted_forecast == 0.0
        assert result.by_stage == []
