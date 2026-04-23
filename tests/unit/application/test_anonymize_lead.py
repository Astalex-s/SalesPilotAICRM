"""
Юнит-тесты AnonymizeLeadUseCase.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.use_cases.anonymize_lead import AnonymizeLeadUseCase
from src.application.exceptions import GdprTargetNotFoundError
from src.domain.entities.lead import Lead
from datetime import datetime, timezone
from src.domain.entities.email_message import EmailMessage
from src.domain.services.lead_anonymization_service import LeadAnonymizationService
from src.domain.value_objects.email import Email


@pytest.fixture
def repos():
    return {
        "lead": AsyncMock(),
        "email": AsyncMock(),
        "activity": AsyncMock(),
        "gdpr_audit": AsyncMock(),
    }


@pytest.fixture
def anon_service():
    svc = MagicMock(spec=LeadAnonymizationService)
    return svc


@pytest.fixture
def use_case(repos, anon_service):
    return AnonymizeLeadUseCase(
        lead_repo=repos["lead"],
        email_repo=repos["email"],
        activity_repo=repos["activity"],
        gdpr_audit_repo=repos["gdpr_audit"],
        anonymization_service=anon_service,
    )


class TestAnonymizeLeadUseCase:
    async def test_raises_if_lead_not_found(self, use_case, repos) -> None:
        repos["lead"].get_by_id.return_value = None

        with pytest.raises(GdprTargetNotFoundError):
            await use_case.execute(uuid4())

    async def test_anonymizes_and_saves_lead(self, use_case, repos, anon_service) -> None:
        lead = Lead.create("Alice", "B", Email("alice@t.com"), uuid4())
        repos["lead"].get_by_id.return_value = lead
        repos["email"].find_by_lead_id.return_value = []
        repos["activity"].gdpr_erase_by_entity.return_value = 0

        await use_case.execute(lead.id)

        anon_service.anonymize.assert_called_once_with(lead)
        repos["lead"].save.assert_called_once_with(lead)

    async def test_deletes_all_emails(self, use_case, repos, anon_service) -> None:
        lead = Lead.create("Bob", "C", Email("bob@t.com"), uuid4())
        now = datetime.now(timezone.utc)
        email1 = EmailMessage.create_inbound("g1", "t1", "a@t.com", ["b@t.com"], "S1", "B1", now)
        email2 = EmailMessage.create_inbound("g2", "t2", "a@t.com", ["b@t.com"], "S2", "B2", now)

        repos["lead"].get_by_id.return_value = lead
        repos["email"].find_by_lead_id.return_value = [email1, email2]
        repos["activity"].gdpr_erase_by_entity.return_value = 3

        result = await use_case.execute(lead.id)

        assert result.emails_deleted == 2
        assert repos["email"].delete.call_count == 2

    async def test_returns_correct_output(self, use_case, repos, anon_service) -> None:
        lead = Lead.create("Carol", "D", Email("carol@t.com"), uuid4())
        repos["lead"].get_by_id.return_value = lead
        repos["email"].find_by_lead_id.return_value = []
        repos["activity"].gdpr_erase_by_entity.return_value = 7

        result = await use_case.execute(lead.id)

        assert result.lead_id == lead.id
        assert result.activities_erased == 7
        assert result.audit_entry_id is not None

    async def test_saves_audit_entry(self, use_case, repos, anon_service) -> None:
        lead = Lead.create("Dave", "E", Email("dave@t.com"), uuid4())
        performer_id = uuid4()
        repos["lead"].get_by_id.return_value = lead
        repos["email"].find_by_lead_id.return_value = []
        repos["activity"].gdpr_erase_by_entity.return_value = 0

        await use_case.execute(lead.id, performed_by_id=performer_id)

        repos["gdpr_audit"].save.assert_called_once()
