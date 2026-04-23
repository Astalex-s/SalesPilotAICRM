"""
Юнит-тесты ListLeadsUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.list_leads import ListLeadsUseCase
from src.application.dtos.lead_dtos import ListLeadsInput
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadStatus


@pytest.fixture
def lead_repo():
    return AsyncMock()


@pytest.fixture
def use_case(lead_repo):
    return ListLeadsUseCase(lead_repo)


@pytest.fixture
def owner_id():
    return uuid4()


def make_lead(email_suffix: str, owner_id):
    return Lead.create("First", "Last", Email(f"test{email_suffix}@t.com"), owner_id)


class TestListLeadsUseCase:
    async def test_no_filters_calls_find_all(self, use_case, lead_repo, owner_id) -> None:
        lead_repo.find_all.return_value = [make_lead("1", owner_id)]

        result = await use_case.execute(ListLeadsInput())

        lead_repo.find_all.assert_called_once()
        lead_repo.find_by_owner.assert_not_called()
        lead_repo.find_by_status.assert_not_called()
        assert len(result) == 1

    async def test_owner_id_filter_calls_find_by_owner(
        self, use_case, lead_repo, owner_id
    ) -> None:
        lead_repo.find_by_owner.return_value = [make_lead("2", owner_id)]

        result = await use_case.execute(ListLeadsInput(owner_id=owner_id))

        lead_repo.find_by_owner.assert_called_once_with(owner_id)
        lead_repo.find_all.assert_not_called()
        assert len(result) == 1

    async def test_status_filter_calls_find_by_status(self, use_case, lead_repo, owner_id) -> None:
        lead_repo.find_by_status.return_value = [make_lead("3", owner_id)]

        result = await use_case.execute(ListLeadsInput(status=LeadStatus.NEW))

        lead_repo.find_by_status.assert_called_once_with(LeadStatus.NEW)
        lead_repo.find_all.assert_not_called()
        assert len(result) == 1

    async def test_owner_id_takes_priority_over_status(
        self, use_case, lead_repo, owner_id
    ) -> None:
        lead_repo.find_by_owner.return_value = []

        await use_case.execute(ListLeadsInput(owner_id=owner_id, status=LeadStatus.NEW))

        lead_repo.find_by_owner.assert_called_once_with(owner_id)
        lead_repo.find_by_status.assert_not_called()

    async def test_returns_lead_output_dtos(self, use_case, lead_repo, owner_id) -> None:
        lead = make_lead("4", owner_id)
        lead_repo.find_all.return_value = [lead]

        result = await use_case.execute(ListLeadsInput())

        assert result[0].id == lead.id
        assert result[0].email == str(lead.email)

    async def test_empty_result(self, use_case, lead_repo) -> None:
        lead_repo.find_all.return_value = []

        result = await use_case.execute(ListLeadsInput())

        assert result == []
