"""
Юнит-тесты AnalyzeLostDealsUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.analyze_lost_deals import AnalyzeLostDealsUseCase
from src.domain.entities.deal import Deal
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


def _make_lost_deal() -> Deal:
    deal = Deal.create("Lost Deal", uuid4(), uuid4(), uuid4(), Money(Decimal("5000")))
    deal.lose()
    return deal


@pytest.fixture
def deal_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def ai_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(deal_repo, ai_service) -> AnalyzeLostDealsUseCase:
    return AnalyzeLostDealsUseCase(deal_repo=deal_repo, ai_service=ai_service)


class TestAnalyzeLostDealsEmpty:
    async def test_returns_empty_analysis_when_no_lost_deals(self, use_case, deal_repo):
        deal_repo.find_by_status.return_value = []

        result = await use_case.execute()
        assert result.total_deals == 0
        assert result.total_lost_value == 0.0
        assert result.loss_patterns == []
        assert "Нет проигранных сделок" in result.recommendations[0]


class TestAnalyzeLostDealsWithData:
    async def test_calls_ai_service_with_deals_context(self, use_case, deal_repo, ai_service):
        deal = _make_lost_deal()
        deal_repo.find_by_status.return_value = [deal]

        mock_result = MagicMock()
        mock_result.total_deals = 1
        mock_result.total_lost_value = 5000.0
        mock_result.loss_patterns = ["Pattern A"]
        mock_result.recommendations = ["Rec 1"]
        mock_result.summary = "One deal lost"
        ai_service.analyze_lost_deals.return_value = mock_result

        result = await use_case.execute()
        ai_service.analyze_lost_deals.assert_called_once()
        assert result.total_deals == 1

    async def test_result_maps_ai_output_correctly(self, use_case, deal_repo, ai_service):
        deal_repo.find_by_status.return_value = [_make_lost_deal()]

        mock_result = MagicMock()
        mock_result.total_deals = 1
        mock_result.total_lost_value = 9999.0
        mock_result.loss_patterns = ["price", "timing"]
        mock_result.recommendations = ["Lower price"]
        mock_result.summary = "Summary here"
        ai_service.analyze_lost_deals.return_value = mock_result

        result = await use_case.execute()
        assert result.summary == "Summary here"
        assert "price" in result.loss_patterns
