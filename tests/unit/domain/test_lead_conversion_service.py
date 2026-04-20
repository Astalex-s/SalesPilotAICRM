"""
Юнит-тесты доменного сервиса LeadConversionService.
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.lead import Lead
from src.domain.exceptions import LeadAlreadyConvertedError, LeadNotQualifiedError
from src.domain.services.lead_conversion_service import LeadConversionService
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import ActivityType, LeadStatus
from src.domain.value_objects.money import Money


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def service() -> LeadConversionService:
    return LeadConversionService()


@pytest.fixture
def qualified_lead() -> Lead:
    lead = Lead.create(
        first_name="Alice",
        last_name="Walker",
        email=Email("alice@corp.com"),
        owner_id=uuid4(),
        company="Corp Ltd",
    )
    lead.qualify()
    return lead


@pytest.fixture
def stage_id():
    return uuid4()


@pytest.fixture
def pipeline_id():
    return uuid4()


# ── Успешная конвертация ────────────────────────────────────────────────────────

class TestLeadConversionServiceHappyPath:
    def test_returns_deal_and_activity(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, activity = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert deal is not None
        assert activity is not None

    def test_deal_has_correct_owner(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, _ = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert deal.owner_id == qualified_lead.owner_id

    def test_deal_has_source_lead_id(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, _ = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert deal.source_lead_id == qualified_lead.id

    def test_deal_title_defaults_to_lead_name(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, _ = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert "Alice Walker" in deal.title

    def test_deal_title_can_be_overridden(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, _ = service.convert(
            qualified_lead,
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            deal_title="Custom Deal Title",
        )
        assert deal.title == "Custom Deal Title"

    def test_deal_value_can_be_set(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        value = Money(Decimal("50000"), "USD")
        deal, _ = service.convert(
            qualified_lead,
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            deal_value=value,
        )
        assert deal.value == value

    def test_lead_is_marked_converted(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        deal, _ = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert qualified_lead.is_converted
        assert qualified_lead.converted_deal_id == deal.id

    def test_activity_type_is_lead_converted(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        _, activity = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert activity.activity_type == ActivityType.LEAD_CONVERTED

    def test_activity_references_lead(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        _, activity = service.convert(
            qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id
        )
        assert activity.entity_id == qualified_lead.id
        assert activity.entity_type == "lead"

    def test_custom_performer_id(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        manager_id = uuid4()
        _, activity = service.convert(
            qualified_lead,
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            performed_by_id=manager_id,
        )
        assert activity.performed_by_id == manager_id


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestLeadConversionServiceGuards:
    def test_unqualified_lead_raises(
        self, service, stage_id, pipeline_id
    ) -> None:
        lead = Lead.create(
            first_name="Bob",
            last_name="Smith",
            email=Email("bob@example.com"),
            owner_id=uuid4(),
        )
        with pytest.raises(LeadNotQualifiedError):
            service.convert(lead, stage_id=stage_id, pipeline_id=pipeline_id)

    def test_contacted_lead_raises(
        self, service, stage_id, pipeline_id
    ) -> None:
        lead = Lead.create(
            first_name="Carl",
            last_name="Jones",
            email=Email("carl@example.com"),
            owner_id=uuid4(),
        )
        lead.contact()
        with pytest.raises(LeadNotQualifiedError):
            service.convert(lead, stage_id=stage_id, pipeline_id=pipeline_id)

    def test_already_converted_lead_raises(
        self, service, qualified_lead, stage_id, pipeline_id
    ) -> None:
        service.convert(qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id)
        with pytest.raises(LeadAlreadyConvertedError):
            service.convert(qualified_lead, stage_id=stage_id, pipeline_id=pipeline_id)
