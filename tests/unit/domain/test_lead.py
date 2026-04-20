"""
Юнит-тесты доменной сущности Lead.
Проверяют: создание, переходы статусов, инварианты, защиту конвертации.
"""
import pytest
from uuid import uuid4

from src.domain.entities.lead import Lead
from src.domain.exceptions import (
    InvalidLeadTransitionError,
    LeadAlreadyConvertedError,
    LeadNotQualifiedError,
)
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource, LeadStatus


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def owner_id():
    return uuid4()


@pytest.fixture
def new_lead(owner_id):
    return Lead.create(
        first_name="John",
        last_name="Doe",
        email=Email("john@example.com"),
        owner_id=owner_id,
        source=LeadSource.WEBSITE,
    )


# ── Создание ───────────────────────────────────────────────────────────────────

class TestLeadCreation:
    def test_creates_with_new_status(self, new_lead: Lead) -> None:
        assert new_lead.status == LeadStatus.NEW

    def test_full_name_property(self, new_lead: Lead) -> None:
        assert new_lead.full_name == "John Doe"

    def test_id_is_generated(self, new_lead: Lead) -> None:
        assert new_lead.id is not None

    def test_empty_first_name_raises(self, owner_id) -> None:
        with pytest.raises(ValueError, match="first name"):
            Lead.create(
                first_name="   ",
                last_name="Doe",
                email=Email("a@b.com"),
                owner_id=owner_id,
            )

    def test_empty_last_name_raises(self, owner_id) -> None:
        with pytest.raises(ValueError, match="last name"):
            Lead.create(
                first_name="John",
                last_name="",
                email=Email("a@b.com"),
                owner_id=owner_id,
            )


# ── Переходы статусов ──────────────────────────────────────────────────────────

class TestLeadTransitions:
    def test_new_can_be_contacted(self, new_lead: Lead) -> None:
        new_lead.contact()
        assert new_lead.status == LeadStatus.CONTACTED

    def test_new_can_be_qualified_directly(self, new_lead: Lead) -> None:
        new_lead.qualify()
        assert new_lead.status == LeadStatus.QUALIFIED

    def test_contacted_can_be_qualified(self, new_lead: Lead) -> None:
        new_lead.contact()
        new_lead.qualify()
        assert new_lead.status == LeadStatus.QUALIFIED

    def test_qualified_can_be_disqualified(self, new_lead: Lead) -> None:
        new_lead.qualify()
        new_lead.disqualify()
        assert new_lead.status == LeadStatus.UNQUALIFIED

    def test_unqualified_can_be_requalified(self, new_lead: Lead) -> None:
        new_lead.disqualify()
        new_lead.qualify()
        assert new_lead.status == LeadStatus.QUALIFIED

    def test_new_cannot_be_converted_directly(self, new_lead: Lead) -> None:
        # mark_converted требует QUALIFIED — прямой переход из NEW запрещён
        with pytest.raises(LeadNotQualifiedError):
            new_lead.mark_converted(deal_id=uuid4())

    def test_invalid_transition_raises(self, new_lead: Lead) -> None:
        # CONTACTED → CONTACTED не является допустимым переходом
        new_lead.contact()
        with pytest.raises(InvalidLeadTransitionError):
            new_lead.contact()

    def test_converted_lead_cannot_change_status(self, new_lead: Lead) -> None:
        new_lead.qualify()
        new_lead.mark_converted(deal_id=uuid4())
        with pytest.raises(LeadAlreadyConvertedError):
            new_lead.qualify()


# ── Защита конвертации ─────────────────────────────────────────────────────────

class TestLeadConversionGuard:
    def test_qualified_lead_can_be_converted(self, new_lead: Lead) -> None:
        new_lead.qualify()
        deal_id = uuid4()
        new_lead.mark_converted(deal_id=deal_id)
        assert new_lead.is_converted
        assert new_lead.converted_deal_id == deal_id

    def test_non_qualified_conversion_raises(self, new_lead: Lead) -> None:
        new_lead.contact()
        with pytest.raises(LeadNotQualifiedError):
            new_lead.mark_converted(deal_id=uuid4())

    def test_double_conversion_raises(self, new_lead: Lead) -> None:
        new_lead.qualify()
        new_lead.mark_converted(deal_id=uuid4())
        with pytest.raises(LeadAlreadyConvertedError):
            new_lead.mark_converted(deal_id=uuid4())

    def test_is_qualified_property(self, new_lead: Lead) -> None:
        assert not new_lead.is_qualified
        new_lead.qualify()
        assert new_lead.is_qualified

    def test_is_converted_property(self, new_lead: Lead) -> None:
        assert not new_lead.is_converted
        new_lead.qualify()
        new_lead.mark_converted(deal_id=uuid4())
        assert new_lead.is_converted
