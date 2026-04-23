"""
Юнит-тесты ListLeadActivitiesUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.list_lead_activities import ListLeadActivitiesUseCase
from src.domain.entities.activity import Activity
from src.domain.value_objects.enums import ActivityType


@pytest.fixture
def activity_repo():
    return AsyncMock()


@pytest.fixture
def use_case(activity_repo):
    return ListLeadActivitiesUseCase(activity_repo)


class TestListLeadActivitiesUseCase:
    async def test_returns_activity_dtos(self, use_case, activity_repo) -> None:
        lead_id = uuid4()
        performer_id = uuid4()
        act = Activity.create("lead", lead_id, ActivityType.NOTE, performer_id, "Test note")
        activity_repo.find_by_entity.return_value = [act]

        result = await use_case.execute(lead_id)

        assert len(result) == 1
        assert result[0].id == act.id
        assert result[0].body == "Test note"
        assert result[0].activity_type == ActivityType.NOTE

    async def test_empty_returns_empty_list(self, use_case, activity_repo) -> None:
        lead_id = uuid4()
        activity_repo.find_by_entity.return_value = []

        result = await use_case.execute(lead_id)

        assert result == []

    async def test_queries_correct_entity(self, use_case, activity_repo) -> None:
        lead_id = uuid4()
        activity_repo.find_by_entity.return_value = []

        await use_case.execute(lead_id)

        activity_repo.find_by_entity.assert_called_once_with("lead", lead_id)

    async def test_multiple_activities_returned(self, use_case, activity_repo) -> None:
        lead_id = uuid4()
        performer_id = uuid4()
        acts = [
            Activity.create("lead", lead_id, ActivityType.NOTE, performer_id, f"Note {i}")
            for i in range(3)
        ]
        activity_repo.find_by_entity.return_value = acts

        result = await use_case.execute(lead_id)

        assert len(result) == 3
