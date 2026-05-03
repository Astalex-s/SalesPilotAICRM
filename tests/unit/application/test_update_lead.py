"""
Юнит-тесты UpdateLeadUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.lead_dtos import UpdateLeadInput
from src.application.exceptions import LeadNotFoundError
from src.application.use_cases.update_lead import UpdateLeadUseCase
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource, LeadStatus


def _make_lead(status: LeadStatus = LeadStatus.NEW) -> Lead:
    lead = Lead.create(
        first_name="Anna",
        last_name="Smith",
        email=Email("anna@example.com"),
        owner_id=uuid4(),
        source=LeadSource.WEBSITE,
    )
    # Force status via direct attribute for testing different starting states
    object.__setattr__(lead, "status", status) if False else None
    lead.status = status
    return lead


@pytest.fixture
def lead_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(lead_repo: AsyncMock) -> UpdateLeadUseCase:
    return UpdateLeadUseCase(lead_repo=lead_repo)


class TestUpdateLeadNotFound:
    async def test_raises_when_lead_not_found(self, use_case, lead_repo):
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(UpdateLeadInput(lead_id=uuid4(), status=LeadStatus.CONTACTED))


class TestUpdateLeadStatus:
    async def test_contact_lead(self, use_case, lead_repo):
        lead = _make_lead(LeadStatus.NEW)
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, status=LeadStatus.CONTACTED))
        assert result.status == LeadStatus.CONTACTED

    async def test_qualify_lead(self, use_case, lead_repo):
        lead = _make_lead(LeadStatus.CONTACTED)
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, status=LeadStatus.QUALIFIED))
        assert result.status == LeadStatus.QUALIFIED

    async def test_disqualify_lead(self, use_case, lead_repo):
        lead = _make_lead(LeadStatus.CONTACTED)
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, status=LeadStatus.UNQUALIFIED))
        assert result.status == LeadStatus.UNQUALIFIED

    async def test_no_status_change(self, use_case, lead_repo):
        lead = _make_lead(LeadStatus.NEW)
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, status=None))
        assert result.status == LeadStatus.NEW

    async def test_new_and_converted_are_ignored(self, use_case, lead_repo):
        lead = _make_lead(LeadStatus.NEW)
        lead_repo.get_by_id.return_value = lead

        # LeadStatus.NEW — match _: pass
        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, status=LeadStatus.NEW))
        assert result.status == LeadStatus.NEW


class TestUpdateLeadNotes:
    async def test_add_notes(self, use_case, lead_repo):
        lead = _make_lead()
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, notes="Important note"))
        assert result.notes == "Important note"

    async def test_no_notes_change_when_none(self, use_case, lead_repo):
        lead = _make_lead()
        lead.add_note("Existing note")
        lead_repo.get_by_id.return_value = lead

        result = await use_case.execute(UpdateLeadInput(lead_id=lead.id, notes=None))
        assert result.notes == "Existing note"
