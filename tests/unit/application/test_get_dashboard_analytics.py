"""
Юнит-тесты GetDashboardAnalyticsUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.lead import Lead
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


@pytest.fixture
def lead_repo():
    return AsyncMock()


@pytest.fixture
def deal_repo():
    return AsyncMock()


@pytest.fixture
def pipeline_repo():
    return AsyncMock()


@pytest.fixture
def use_case(lead_repo, deal_repo, pipeline_repo):
    return GetDashboardAnalyticsUseCase(lead_repo, deal_repo, pipeline_repo)


@pytest.fixture
def owner_id():
    return uuid4()


class TestGetDashboardAnalyticsEmpty:
    async def test_empty_returns_zeros(self, use_case, lead_repo, deal_repo, pipeline_repo) -> None:
        lead_repo.find_all.return_value = []
        deal_repo.find_all.return_value = []
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.total_leads == 0
        assert result.conversion_rate == 0.0
        assert result.total_deals == 0
        assert result.open_deals == 0
        assert result.pipeline_value == 0.0
        assert result.revenue_forecast == 0.0


class TestGetDashboardAnalyticsMetrics:
    async def test_conversion_rate(
        self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id
    ) -> None:
        leads = [
            Lead.create("L1", "S", Email("l1@t.com"), owner_id),
            Lead.create("L2", "S", Email("l2@t.com"), owner_id),
        ]
        leads[0].qualify()
        leads[0].mark_converted(uuid4())
        lead_repo.find_all.return_value = leads
        deal_repo.find_all.return_value = []
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.total_leads == 2
        assert result.conversion_rate == 50.0

    async def test_pipeline_value_only_open_deals(
        self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id
    ) -> None:
        stage_id = uuid4()
        pipeline_id = uuid4()
        open_deal = Deal.create("Open", owner_id, stage_id, pipeline_id, Money(Decimal("600")))
        won_deal = Deal.create("Won", owner_id, stage_id, pipeline_id, Money(Decimal("400")))
        won_deal.win()

        lead_repo.find_all.return_value = []
        deal_repo.find_all.return_value = [open_deal, won_deal]
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.pipeline_value == 600.0
        assert result.open_deals == 1
        assert result.total_deals == 2

    async def test_revenue_forecast_uses_stage_probability(
        self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id
    ) -> None:
        pipeline = Pipeline.create("Sales", owner_id)
        stage = Stage.create(pipeline.id, "Qualified", 1, 0.6)
        pipeline.add_stage(stage)

        deal = Deal.create("Deal", owner_id, stage.id, pipeline.id, Money(Decimal("1000")))

        lead_repo.find_all.return_value = []
        deal_repo.find_all.return_value = [deal]
        pipeline_repo.find_active.return_value = [pipeline]

        result = await use_case.execute()

        assert result.revenue_forecast == 600.0  # 1000 * 0.6

    async def test_leads_by_status_breakdown(
        self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id
    ) -> None:
        leads = [
            Lead.create("N1", "S", Email("n1@t.com"), owner_id),  # new
            Lead.create("C1", "S", Email("c1@t.com"), owner_id),  # contacted
        ]
        leads[1].contact()
        lead_repo.find_all.return_value = leads
        deal_repo.find_all.return_value = []
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.leads_by_status.new == 1
        assert result.leads_by_status.contacted == 1

    async def test_deals_by_status_breakdown(
        self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id
    ) -> None:
        stage_id, pipeline_id = uuid4(), uuid4()
        open_d = Deal.create("O", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
        won_d = Deal.create("W", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
        lost_d = Deal.create("L", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
        won_d.win()
        lost_d.lose()

        lead_repo.find_all.return_value = []
        deal_repo.find_all.return_value = [open_d, won_d, lost_d]
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert result.deals_by_status.open == 1
        assert result.deals_by_status.won == 1
        assert result.deals_by_status.lost == 1
