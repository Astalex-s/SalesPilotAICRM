"""
Юнит-тесты для аналитических Use Cases.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.get_analytics_overview import GetAnalyticsOverviewUseCase
from src.application.dtos.analytics_dtos import AnalyticsOverviewOutput
from src.domain.entities.lead import Lead
from src.domain.entities.deal import Deal
from src.domain.entities.pipeline import Pipeline
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.domain.value_objects.enums import LeadStatus, DealStatus

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
def owner_id():
    return uuid4()

@pytest.fixture
def use_case(lead_repo, deal_repo, pipeline_repo):
    return GetAnalyticsOverviewUseCase(lead_repo, deal_repo, pipeline_repo)

class TestGetAnalyticsOverview:
    async def test_empty_data_returns_zeros(self, use_case, lead_repo, deal_repo, pipeline_repo):
        lead_repo.find_all.return_value = []
        deal_repo.find_all.return_value = []
        pipeline_repo.find_active.return_value = []

        result = await use_case.execute()

        assert isinstance(result, AnalyticsOverviewOutput)
        assert result.total_leads == 0
        assert result.conversion_rate == 0.0
        assert result.total_deals == 0
        assert result.overall_win_rate == 0.0

    async def test_calculates_correct_metrics(self, use_case, lead_repo, deal_repo, pipeline_repo, owner_id):
        # 4 лида, 1 сконвертирован -> 25% conversion
        leads = [
            Lead.create("L1", "S1", Email("l1@t.com"), owner_id),
            Lead.create("L2", "S2", Email("l2@t.com"), owner_id),
            Lead.create("L3", "S3", Email("l3@t.com"), owner_id),
            Lead.create("L4", "S4", Email("l4@t.com"), owner_id),
        ]
        leads[0].qualify()
        leads[0].mark_converted(deal_id=uuid4())
        lead_repo.find_all.return_value = leads

        pipeline = Pipeline.create("Sales", owner_id)
        pipeline_id = pipeline.id  # использовать реальный id воронки
        pipeline_repo.find_active.return_value = [pipeline]

        # 3 сделки: 1 WON, 1 LOST, 1 OPEN. Value open = 1000
        stage_id = uuid4()  # только для поля stage_id у сделки; analytics не использует stage
        deals = [
            Deal.create("D1", owner_id, stage_id, pipeline_id, Money(Decimal("1000"))),
            Deal.create("D2", owner_id, stage_id, pipeline_id, Money(Decimal("500"))),
            Deal.create("D3", owner_id, stage_id, pipeline_id, Money(Decimal("500"))),
        ]
        deals[1].win()
        deals[2].lose()
        deal_repo.find_all.return_value = deals

        result = await use_case.execute()

        assert result.total_leads == 4
        assert result.conversion_rate == 25.0
        assert result.total_deals == 3
        assert result.overall_win_rate == 50.0  # 1 won / (1 won + 1 lost)
        assert result.avg_deal_size == 1000.0

        # Проверка статистики по воронке
        assert len(result.pipeline_stats) == 1
        stats = result.pipeline_stats[0]
        assert stats.pipeline_name == "Sales"
        assert stats.won_revenue == 500.0
        assert stats.pipeline_value == 1000.0
