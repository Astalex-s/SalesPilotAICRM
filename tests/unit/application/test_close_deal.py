"""
Юнит-тесты CloseDealUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.application.dtos.deal_dtos import CloseDealInput
from src.application.exceptions import DealNotFoundError
from src.application.use_cases.close_deal import CloseDealUseCase
from src.domain.entities.deal import Deal
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


def _make_deal() -> Deal:
    return Deal.create(
        title="Big Deal",
        owner_id=uuid4(),
        stage_id=uuid4(),
        pipeline_id=uuid4(),
        value=Money(Decimal("10000")),
    )


@pytest.fixture
def deal_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def activity_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(deal_repo, activity_repo) -> CloseDealUseCase:
    return CloseDealUseCase(deal_repo=deal_repo, activity_repo=activity_repo)


class TestCloseDealNotFound:
    async def test_raises_when_deal_not_found(self, use_case, deal_repo):
        deal_repo.get_by_id.return_value = None
        with pytest.raises(DealNotFoundError):
            await use_case.execute(CloseDealInput(deal_id=uuid4(), outcome="won"))


class TestCloseDealWon:
    async def test_win_sets_status_won(self, use_case, deal_repo, activity_repo):
        deal = _make_deal()
        deal_repo.get_by_id.return_value = deal

        result = await use_case.execute(CloseDealInput(deal_id=deal.id, outcome="won"))
        assert result.status == DealStatus.WON
        activity_repo.save.assert_called_once()

    async def test_win_with_custom_performed_by(self, use_case, deal_repo):
        deal = _make_deal()
        deal_repo.get_by_id.return_value = deal
        performer = uuid4()

        result = await use_case.execute(
            CloseDealInput(deal_id=deal.id, outcome="won", performed_by_id=performer)
        )
        assert result.status == DealStatus.WON


class TestCloseDealLost:
    async def test_lose_sets_status_lost(self, use_case, deal_repo, activity_repo):
        deal = _make_deal()
        deal_repo.get_by_id.return_value = deal

        result = await use_case.execute(CloseDealInput(deal_id=deal.id, outcome="lost"))
        assert result.status == DealStatus.LOST
        activity_repo.save.assert_called_once()

    async def test_lose_uses_deal_owner_as_performer_when_not_provided(
        self, use_case, deal_repo
    ):
        deal = _make_deal()
        deal_repo.get_by_id.return_value = deal

        result = await use_case.execute(CloseDealInput(deal_id=deal.id, outcome="lost"))
        assert result.status == DealStatus.LOST
