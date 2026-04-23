"""
Юнит-тесты ListDealsUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.list_deals import ListDealsUseCase
from src.application.dtos.deal_dtos import ListDealsInput
from src.domain.entities.deal import Deal
from src.domain.value_objects.money import Money


@pytest.fixture
def deal_repo():
    return AsyncMock()


@pytest.fixture
def use_case(deal_repo):
    return ListDealsUseCase(deal_repo)


@pytest.fixture
def owner_id():
    return uuid4()


def make_deal(owner_id, pipeline_id=None, stage_id=None):
    return Deal.create(
        "Test Deal",
        owner_id,
        stage_id or uuid4(),
        pipeline_id or uuid4(),
        Money(Decimal("100")),
    )


class TestListDealsUseCase:
    async def test_no_filters_calls_find_all(self, use_case, deal_repo, owner_id) -> None:
        deal_repo.find_all.return_value = [make_deal(owner_id)]

        result = await use_case.execute(ListDealsInput())

        deal_repo.find_all.assert_called_once()
        assert len(result) == 1

    async def test_pipeline_id_filter(self, use_case, deal_repo, owner_id) -> None:
        pipeline_id = uuid4()
        deal_repo.find_by_pipeline.return_value = [make_deal(owner_id, pipeline_id=pipeline_id)]

        result = await use_case.execute(ListDealsInput(pipeline_id=pipeline_id))

        deal_repo.find_by_pipeline.assert_called_once_with(pipeline_id)
        deal_repo.find_all.assert_not_called()
        assert len(result) == 1

    async def test_stage_id_filter(self, use_case, deal_repo, owner_id) -> None:
        stage_id = uuid4()
        deal_repo.find_by_stage.return_value = [make_deal(owner_id, stage_id=stage_id)]

        result = await use_case.execute(ListDealsInput(stage_id=stage_id))

        deal_repo.find_by_stage.assert_called_once_with(stage_id)
        deal_repo.find_all.assert_not_called()

    async def test_owner_id_filter(self, use_case, deal_repo, owner_id) -> None:
        deal_repo.find_by_owner.return_value = [make_deal(owner_id)]

        result = await use_case.execute(ListDealsInput(owner_id=owner_id))

        deal_repo.find_by_owner.assert_called_once_with(owner_id)

    async def test_pipeline_id_takes_priority(self, use_case, deal_repo, owner_id) -> None:
        pipeline_id = uuid4()
        deal_repo.find_by_pipeline.return_value = []

        await use_case.execute(ListDealsInput(pipeline_id=pipeline_id, stage_id=uuid4()))

        deal_repo.find_by_pipeline.assert_called_once_with(pipeline_id)
        deal_repo.find_by_stage.assert_not_called()

    async def test_stage_id_over_owner_id(self, use_case, deal_repo, owner_id) -> None:
        stage_id = uuid4()
        deal_repo.find_by_stage.return_value = []

        await use_case.execute(ListDealsInput(stage_id=stage_id, owner_id=owner_id))

        deal_repo.find_by_stage.assert_called_once_with(stage_id)
        deal_repo.find_by_owner.assert_not_called()

    async def test_returns_deal_output_dtos(self, use_case, deal_repo, owner_id) -> None:
        deal = make_deal(owner_id)
        deal_repo.find_all.return_value = [deal]

        result = await use_case.execute(ListDealsInput())

        assert result[0].id == deal.id
        assert result[0].title == deal.title
