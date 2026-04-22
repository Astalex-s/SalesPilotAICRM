"""Юнит-тесты use case NotifyNewLeadUseCase.
ITelegramService заменён AsyncMock — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.telegram_dtos import NotifyNewLeadInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.notify_new_lead import NotifyNewLeadUseCase
from src.domain.value_objects.enums import LeadSource


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def telegram_service() -> MagicMock:
    """Мок ITelegramService — бот настроен по умолчанию."""
    svc = MagicMock()
    svc.is_configured.return_value = True
    svc.notify = AsyncMock()
    return svc


@pytest.fixture
def use_case(telegram_service: MagicMock) -> NotifyNewLeadUseCase:
    return NotifyNewLeadUseCase(telegram_service=telegram_service)


@pytest.fixture
def valid_input() -> NotifyNewLeadInput:
    return NotifyNewLeadInput(
        lead_id=uuid4(),
        first_name="Иван",
        last_name="Петров",
        email="ivan@example.com",
        company="ООО Ромашка",
        source=LeadSource.WEBSITE,
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestNotifyNewLeadHappyPath:
    async def test_notify_called_once(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """notify вызывается ровно один раз при корректных данных."""
        await use_case.execute(valid_input)
        telegram_service.notify.assert_called_once()

    async def test_message_contains_full_name(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит имя и фамилию лида."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert "Иван" in text
        assert "Петров" in text

    async def test_message_contains_email(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит email лида."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert "ivan@example.com" in text

    async def test_message_contains_company(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит название компании."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert "ООО Ромашка" in text

    async def test_message_contains_source(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит источник лида."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert LeadSource.WEBSITE.value in text

    async def test_message_without_company_shows_dash(
        self,
        use_case: NotifyNewLeadUseCase,
        telegram_service: MagicMock,
    ) -> None:
        """Если компания не указана — в тексте отображается прочерк."""
        data = NotifyNewLeadInput(
            lead_id=uuid4(),
            first_name="Анна",
            last_name="Сидорова",
            email="anna@example.com",
            company=None,
            source=LeadSource.REFERRAL,
        )
        await use_case.execute(data)
        text: str = telegram_service.notify.call_args[0][0]
        assert "—" in text


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestNotifyNewLeadGuards:
    async def test_not_configured_raises(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """TelegramNotConfiguredError если сервис не настроен."""
        telegram_service.is_configured.return_value = False
        with pytest.raises(TelegramNotConfiguredError):
            await use_case.execute(valid_input)

    async def test_not_configured_does_not_call_notify(
        self,
        use_case: NotifyNewLeadUseCase,
        valid_input: NotifyNewLeadInput,
        telegram_service: MagicMock,
    ) -> None:
        """При отсутствии конфигурации notify не вызывается."""
        telegram_service.is_configured.return_value = False
        with pytest.raises(TelegramNotConfiguredError):
            await use_case.execute(valid_input)
        telegram_service.notify.assert_not_called()
