"""
Юнит-тесты ApplyRetentionPolicyUseCase.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.apply_retention_policy import ApplyRetentionPolicyUseCase
from src.domain.entities.lead import Lead
from src.domain.entities.deal import Deal
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource
from src.domain.value_objects.money import Money


def _old_lead() -> Lead:
    lead = Lead.create(
        first_name="Old",
        last_name="Lead",
        email=Email(f"old_{uuid4().hex[:6]}@example.com"),
        owner_id=uuid4(),
        source=LeadSource.WEBSITE,
    )
    # Force old created_at
    lead.created_at = datetime.now(timezone.utc) - timedelta(days=800)
    return lead


def _old_deal() -> Deal:
    deal = Deal.create("Old Deal", uuid4(), uuid4(), uuid4(), Money(Decimal("1000")))
    deal.created_at = datetime.now(timezone.utc) - timedelta(days=800)
    return deal


def _recent_lead() -> Lead:
    return Lead.create(
        first_name="New",
        last_name="Lead",
        email=Email(f"new_{uuid4().hex[:6]}@example.com"),
        owner_id=uuid4(),
        source=LeadSource.WEBSITE,
    )


@pytest.fixture
def lead_repo():
    repo = AsyncMock()
    repo.find_all.return_value = []
    return repo


@pytest.fixture
def deal_repo():
    repo = AsyncMock()
    repo.find_all.return_value = []
    return repo


@pytest.fixture
def email_repo():
    repo = AsyncMock()
    repo.find_by_lead_id.return_value = []
    return repo


@pytest.fixture
def activity_repo():
    repo = AsyncMock()
    repo.gdpr_erase_by_entity.return_value = 0
    return repo


@pytest.fixture
def gdpr_audit_repo():
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(lead_repo, deal_repo, email_repo, activity_repo, gdpr_audit_repo):
    return ApplyRetentionPolicyUseCase(
        lead_repo=lead_repo,
        deal_repo=deal_repo,
        email_repo=email_repo,
        activity_repo=activity_repo,
        gdpr_audit_repo=gdpr_audit_repo,
    )


class TestRetentionPolicyNoData:
    async def test_returns_zero_counts_when_no_data(self, use_case):
        result = await use_case.execute(retention_days=730)
        assert result.leads_deleted == 0
        assert result.deals_deleted == 0
        assert result.retention_days == 730


class TestRetentionPolicyWithOldData:
    async def test_deletes_old_leads(self, use_case, lead_repo):
        old = _old_lead()
        lead_repo.find_all.return_value = [old]

        result = await use_case.execute(retention_days=365)
        assert result.leads_deleted == 1
        lead_repo.delete.assert_called_once_with(old.id)

    async def test_deletes_old_deals(self, use_case, deal_repo):
        old = _old_deal()
        deal_repo.find_all.return_value = [old]

        result = await use_case.execute(retention_days=365)
        assert result.deals_deleted == 1
        deal_repo.delete.assert_called_once_with(old.id)

    async def test_preserves_recent_data(self, use_case, lead_repo):
        recent = _recent_lead()
        lead_repo.find_all.return_value = [recent]

        result = await use_case.execute(retention_days=365)
        assert result.leads_deleted == 0
        lead_repo.delete.assert_not_called()

    async def test_saves_audit_entry(self, use_case, gdpr_audit_repo):
        await use_case.execute(retention_days=730)
        gdpr_audit_repo.save.assert_called_once()

    async def test_counts_erased_activities(self, use_case, lead_repo, activity_repo):
        old = _old_lead()
        lead_repo.find_all.return_value = [old]
        activity_repo.gdpr_erase_by_entity.return_value = 5

        result = await use_case.execute(retention_days=365)
        assert result.activities_erased == 5
