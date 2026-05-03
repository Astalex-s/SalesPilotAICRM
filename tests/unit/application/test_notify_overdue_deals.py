"""
Юнит-тесты NotifyOverdueDealsUseCase.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.notify_overdue_deals import NotifyOverdueDealsUseCase
from src.domain.entities.deal import Deal
from src.domain.value_objects.money import Money


def _make_overdue_deal(days_overdue: int = 5) -> Deal:
    deal = Deal.create("Overdue Deal", uuid4(), uuid4(), uuid4(), Money(Decimal("3000")))
    deal.expected_close_date = datetime.now(timezone.utc) - timedelta(days=days_overdue)
    return deal


@pytest.fixture
def telegram_service() -> MagicMock:
    svc = MagicMock()
    svc.is_configured.return_value = True
    svc.notify = AsyncMock()
    return svc


@pytest.fixture
def deal_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(telegram_service, deal_repo) -> NotifyOverdueDealsUseCase:
    return NotifyOverdueDealsUseCase(telegram_service=telegram_service, deal_repo=deal_repo)


class TestNotifyOverdueDealsNotConfigured:
    async def test_raises_when_telegram_not_configured(self, telegram_service, deal_repo):
        telegram_service.is_configured.return_value = False
        uc = NotifyOverdueDealsUseCase(telegram_service=telegram_service, deal_repo=deal_repo)

        with pytest.raises(TelegramNotConfiguredError):
            await uc.execute()


class TestNotifyOverdueDealsEmpty:
    async def test_returns_zero_when_no_overdue(self, use_case, deal_repo, telegram_service):
        deal_repo.find_overdue.return_value = []

        count = await use_case.execute()
        assert count == 0
        telegram_service.notify.assert_not_called()


class TestNotifyOverdueDealsWithDeals:
    async def test_sends_notification_and_returns_count(self, use_case, deal_repo, telegram_service):
        overdue = [_make_overdue_deal(), _make_overdue_deal()]
        deal_repo.find_overdue.return_value = overdue

        count = await use_case.execute()
        assert count == 2
        telegram_service.notify.assert_called_once()

    async def test_message_contains_overdue_info(self, use_case, deal_repo, telegram_service):
        deal = _make_overdue_deal(days_overdue=3)
        deal.title = "Important Deal"
        deal_repo.find_overdue.return_value = [deal]

        await use_case.execute()

        message = telegram_service.notify.call_args[0][0]
        assert "Important Deal" in message

    async def test_truncates_to_max_deals(self, use_case, deal_repo, telegram_service):
        # Create 25 overdue deals (more than _MAX_DEALS_PER_MESSAGE = 20)
        overdue = [_make_overdue_deal() for _ in range(25)]
        deal_repo.find_overdue.return_value = overdue

        count = await use_case.execute()
        assert count == 25
        message = telegram_service.notify.call_args[0][0]
        assert "...и ещё" in message

    async def test_deal_with_no_close_date(self, use_case, deal_repo, telegram_service):
        deal = _make_overdue_deal()
        deal.expected_close_date = None
        deal_repo.find_overdue.return_value = [deal]

        await use_case.execute()
        telegram_service.notify.assert_called_once()
