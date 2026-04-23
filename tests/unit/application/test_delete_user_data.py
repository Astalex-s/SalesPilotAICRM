"""
Юнит-тесты для GDPR Use Case DeleteUserDataUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.delete_user_data import DeleteUserDataUseCase
from src.application.exceptions import GdprTargetNotFoundError
from datetime import datetime, timezone
from src.domain.entities.lead import Lead
from src.domain.entities.deal import Deal
from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.email import Email
from decimal import Decimal
from src.domain.value_objects.money import Money
from src.domain.value_objects.enums import LeadSource

@pytest.fixture
def repo_mocks():
    return {
        "lead": AsyncMock(),
        "deal": AsyncMock(),
        "email": AsyncMock(),
        "activity": AsyncMock(),
        "gdpr_audit": AsyncMock(),
    }

@pytest.fixture
def use_case(repo_mocks):
    return DeleteUserDataUseCase(
        lead_repo=repo_mocks["lead"],
        deal_repo=repo_mocks["deal"],
        email_repo=repo_mocks["email"],
        activity_repo=repo_mocks["activity"],
        gdpr_audit_repo=repo_mocks["gdpr_audit"],
    )

class TestDeleteUserData:
    async def test_raises_error_if_nothing_found(self, use_case, repo_mocks):
        user_id = uuid4()
        repo_mocks["lead"].find_by_owner.return_value = []
        repo_mocks["deal"].find_by_owner.return_value = []

        with pytest.raises(GdprTargetNotFoundError):
            await use_case.execute(user_id)

    async def test_successful_deletion_flow(self, use_case, repo_mocks):
        user_id = uuid4()
        lead = Lead.create("Alice", "W", Email("a@t.com"), user_id)
        deal = Deal.create("Deal 1", user_id, uuid4(), uuid4(), Money(Decimal("100")))
        now = datetime.now(timezone.utc)
        email = EmailMessage.create_inbound("gmail_1", "thread_1", "a@t.com", ["me@t.com"], "Hello", "Body", now)

        repo_mocks["lead"].find_by_owner.return_value = [lead]
        repo_mocks["deal"].find_by_owner.return_value = [deal]
        repo_mocks["email"].find_by_lead_id.return_value = [email]
        repo_mocks["activity"].gdpr_erase_by_entity.return_value = 5  # 5 activities erased
        repo_mocks["activity"].gdpr_erase_by_performer.return_value = 2

        result = await use_case.execute(user_id)

        assert result.user_id == user_id
        assert result.leads_deleted == 1
        assert result.deals_deleted == 1
        assert result.emails_deleted == 1
        assert result.activities_erased == 12  # 5 (lead) + 5 (deal) + 2 (performer)

        # Проверка вызовов репозиториев
        repo_mocks["email"].delete.assert_called_once_with(email.id)
        repo_mocks["lead"].delete.assert_called_once_with(lead.id)
        repo_mocks["deal"].delete.assert_called_once_with(deal.id)
        repo_mocks["gdpr_audit"].save.assert_called_once()
