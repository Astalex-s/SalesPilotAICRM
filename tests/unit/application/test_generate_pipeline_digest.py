"""
Юнит-тесты GeneratePipelineDigestUseCase.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.exceptions import PipelineNotFoundError
from src.application.use_cases.generate_pipeline_digest import GeneratePipelineDigestUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.pipeline import Pipeline
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


def _make_pipeline() -> Pipeline:
    return Pipeline.create(name="Sales Pipeline", owner_id=uuid4())


def _make_deal(pipeline_id, status: DealStatus = DealStatus.OPEN, amount: float = 5000.0) -> Deal:
    deal = Deal.create("Test Deal", uuid4(), uuid4(), pipeline_id, Money(Decimal(str(amount))))
    if status == DealStatus.WON:
        deal.win()
    elif status == DealStatus.LOST:
        deal.lose()
    return deal


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def deal_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def ai_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(pipeline_repo, deal_repo, ai_service) -> GeneratePipelineDigestUseCase:
    return GeneratePipelineDigestUseCase(
        deal_repo=deal_repo,
        pipeline_repo=pipeline_repo,
        ai_service=ai_service,
    )


def _mock_ai_result(**kwargs) -> MagicMock:
    result = MagicMock()
    result.summary = kwargs.get("summary", "Weekly digest")
    result.key_metrics = kwargs.get("key_metrics", ["Metric 1"])
    result.risks = kwargs.get("risks", [])
    result.opportunities = kwargs.get("opportunities", [])
    result.focus_deals = kwargs.get("focus_deals", [])
    return result


class TestGenerateDigestNotFound:
    async def test_raises_when_pipeline_not_found(self, use_case, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(uuid4())


class TestGenerateDigestNoDeals:
    async def test_empty_pipeline_returns_digest(self, use_case, pipeline_repo, deal_repo, ai_service):
        pipeline = _make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline
        deal_repo.find_by_pipeline.return_value = []
        ai_service.generate_pipeline_digest.return_value = _mock_ai_result()

        result = await use_case.execute(pipeline.id)
        assert result.pipeline_id == pipeline.id
        ai_service.generate_pipeline_digest.assert_called_once()


class TestGenerateDigestWithDeals:
    async def test_calculates_win_rate(self, use_case, pipeline_repo, deal_repo, ai_service):
        pipeline = _make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        won = _make_deal(pipeline.id, DealStatus.WON)
        lost = _make_deal(pipeline.id, DealStatus.LOST)
        open_deal = _make_deal(pipeline.id, DealStatus.OPEN)
        deal_repo.find_by_pipeline.return_value = [won, lost, open_deal]
        ai_service.generate_pipeline_digest.return_value = _mock_ai_result()

        await use_case.execute(pipeline.id)

        call_kwargs = ai_service.generate_pipeline_digest.call_args[0][0]
        assert call_kwargs["win_rate"] == 50.0
        assert call_kwargs["open_deals"] == 1

    async def test_identifies_stale_deals(self, use_case, pipeline_repo, deal_repo, ai_service):
        pipeline = _make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline

        stale_deal = _make_deal(pipeline.id, DealStatus.OPEN)
        stale_deal.updated_at = datetime.now(timezone.utc) - timedelta(days=20)
        deal_repo.find_by_pipeline.return_value = [stale_deal]
        ai_service.generate_pipeline_digest.return_value = _mock_ai_result()

        await use_case.execute(pipeline.id)

        call_kwargs = ai_service.generate_pipeline_digest.call_args[0][0]
        assert "нет" not in call_kwargs["stale_deals"]

    async def test_result_maps_ai_output(self, use_case, pipeline_repo, deal_repo, ai_service):
        pipeline = _make_pipeline()
        pipeline_repo.get_by_id.return_value = pipeline
        deal_repo.find_by_pipeline.return_value = []
        ai_service.generate_pipeline_digest.return_value = _mock_ai_result(
            summary="Great pipeline!",
            risks=["Low win rate"],
        )

        result = await use_case.execute(pipeline.id)
        assert result.summary == "Great pipeline!"
        assert "Low win rate" in result.risks
        assert result.pipeline_name == pipeline.name
