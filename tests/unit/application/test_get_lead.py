"""
Юнит-тесты GetLeadUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.get_lead import GetLeadUseCase
from src.application.dtos.lead_dtos import GetLeadInput
from src.application.exceptions import LeadNotFoundError
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email


@pytest.fixture
def lead_repo():
    return AsyncMock()


@pytest.fixture
def use_case(lead_repo):
    return GetLeadUseCase(lead_repo)


class TestGetLeadUseCase:
    async def test_returns_lead_dto(self, use_case, lead_repo) -> None:
        owner_id = uuid4()
        lead = Lead.create("John", "Doe", Email("john@t.com"), owner_id)
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(GetLeadInput(lead_id=lead.id))

        assert result.id == lead.id
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john@t.com"
        assert result.owner_id == owner_id

    async def test_raises_if_not_found(self, use_case, lead_repo) -> None:
        lead_repo.get_by_id.return_value = None
        missing_id = uuid4()

        with pytest.raises(LeadNotFoundError):
            await use_case.execute(GetLeadInput(lead_id=missing_id))

    async def test_queries_correct_id(self, use_case, lead_repo) -> None:
        lead_id = uuid4()
        lead_repo.get_by_id.return_value = Lead.create("A", "B", Email("a@b.com"), uuid4())

        await use_case.execute(GetLeadInput(lead_id=lead_id))

        lead_repo.get_by_id.assert_called_once_with(lead_id)
