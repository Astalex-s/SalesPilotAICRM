"""
Юнит-тесты NotifyNewDealUseCase и CreatePipelineUseCase.
"""
from __future__ import annotations

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.pipeline_dtos import CreatePipelineInput
from src.application.dtos.telegram_dtos import NotifyNewDealInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.create_pipeline import CreatePipelineUseCase
from src.application.use_cases.notify_new_deal import NotifyNewDealUseCase


# ── NotifyNewDealUseCase ───────────────────────────────────────────────────────

class TestNotifyNewDeal:
    @pytest.fixture
    def telegram_service(self):
        svc = MagicMock()
        svc.is_configured.return_value = True
        svc.notify = AsyncMock()
        return svc

    def _input(self) -> NotifyNewDealInput:
        return NotifyNewDealInput(
            deal_id=uuid4(),
            deal_title="Big Deal",
            lead_name="John Doe",
            value_amount=Decimal("50000"),
            value_currency="USD",
        )

    async def test_raises_when_not_configured(self, telegram_service):
        telegram_service.is_configured.return_value = False
        uc = NotifyNewDealUseCase(telegram_service=telegram_service)
        with pytest.raises(TelegramNotConfiguredError):
            await uc.execute(self._input())

    async def test_sends_notification(self, telegram_service):
        uc = NotifyNewDealUseCase(telegram_service=telegram_service)
        await uc.execute(self._input())
        telegram_service.notify.assert_called_once()
        msg = telegram_service.notify.call_args[0][0]
        assert "Big Deal" in msg
        assert "John Doe" in msg


# ── CreatePipelineUseCase ──────────────────────────────────────────────────────

class TestCreatePipeline:
    async def test_creates_and_returns_pipeline(self):
        from src.domain.entities.pipeline import Pipeline
        pipeline_repo = AsyncMock()
        pipeline = Pipeline.create(name="Sales", owner_id=uuid4())
        pipeline_repo.save.return_value = pipeline

        uc = CreatePipelineUseCase(pipeline_repo=pipeline_repo)
        result = await uc.execute(CreatePipelineInput(name="Sales"), owner_id=pipeline.owner_id)

        assert result.name == "Sales"
        pipeline_repo.save.assert_called_once()
