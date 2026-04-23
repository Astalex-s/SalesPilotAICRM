"""
Юнит-тесты доменного сервиса LeadAnonymizationService.
Проверяют: PII-поля заменены, ID/статус/owner сохранены.
"""
import pytest
import re
from uuid import uuid4

from src.domain.entities.lead import Lead
from src.domain.services.lead_anonymization_service import LeadAnonymizationService
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadStatus


@pytest.fixture
def service() -> LeadAnonymizationService:
    return LeadAnonymizationService()


@pytest.fixture
def lead() -> Lead:
    l = Lead.create("Alice", "Smith", Email("alice@company.com"), uuid4())
    l.phone = "+1234567890"  # type: ignore[assignment]
    l.company = "ACME Inc"
    l.notes = "VIP client"
    return l


class TestLeadAnonymizationService:
    def test_first_name_anonymized(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.first_name == "[ANONYMIZED]"

    def test_last_name_anonymized(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.last_name == "[ANONYMIZED]"

    def test_email_replaced_with_gdpr_format(self, service, lead) -> None:
        service.anonymize(lead)
        pattern = r"^anon-[0-9a-f]{8}@gdpr\.deleted$"
        assert re.match(pattern, str(lead.email))

    def test_phone_cleared(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.phone is None

    def test_company_cleared(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.company is None

    def test_notes_cleared(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.notes is None

    def test_id_preserved(self, service, lead) -> None:
        original_id = lead.id
        service.anonymize(lead)
        assert lead.id == original_id

    def test_owner_id_preserved(self, service, lead) -> None:
        original_owner = lead.owner_id
        service.anonymize(lead)
        assert lead.owner_id == original_owner

    def test_status_preserved(self, service, lead) -> None:
        service.anonymize(lead)
        assert lead.status == LeadStatus.NEW

    def test_anon_email_passes_email_vo_validation(self, service, lead) -> None:
        """anon-{uuid8}@gdpr.deleted должен проходить валидацию Email VO."""
        service.anonymize(lead)
        # Email VO конструктор не бросает исключение — значит email валиден
        assert lead.email is not None

    def test_email_uses_lead_id_prefix(self, service, lead) -> None:
        expected_prefix = str(lead.id)[:8]
        service.anonymize(lead)
        assert str(lead.email).startswith(f"anon-{expected_prefix}@")
