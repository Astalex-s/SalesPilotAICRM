"""
Интеграционные тесты SqlLeadRepository.
"""
import pytest
from uuid import uuid4
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadStatus
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository

@pytest.mark.asyncio
async def test_lead_repository_save_and_get(db_session):
    repo = SqlLeadRepository(db_session)
    owner_id = uuid4()
    lead = Lead.create("Test", "User", Email("test@repo.com"), owner_id)

    # Save
    saved_lead = await repo.save(lead)
    assert saved_lead.id == lead.id

    # Get by ID
    found_lead = await repo.get_by_id(lead.id)
    assert found_lead is not None
    assert found_lead.email.value == "test@repo.com"
    assert found_lead.owner_id == owner_id

@pytest.mark.asyncio
async def test_lead_repository_find_by_email(db_session):
    repo = SqlLeadRepository(db_session)
    email_str = "unique@test.com"
    lead = Lead.create("N", "N", Email(email_str), uuid4())
    await repo.save(lead)

    found = await repo.find_by_email(email_str)
    assert found is not None
    assert found.id == lead.id

    not_found = await repo.find_by_email("wrong@test.com")
    assert not_found is None

@pytest.mark.asyncio
async def test_lead_repository_delete(db_session):
    repo = SqlLeadRepository(db_session)
    lead = Lead.create("D", "D", Email("d@t.com"), uuid4())
    await repo.save(lead)

    await repo.delete(lead.id)
    found = await repo.get_by_id(lead.id)
    assert found is None
