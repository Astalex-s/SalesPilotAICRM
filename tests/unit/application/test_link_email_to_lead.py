"""Юнит-тесты use case LinkEmailToLeadUseCase.
Репозитории заменены AsyncMock — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from src.application.dtos.email_message_dtos import EmailMessageOutput, LinkEmailToLeadInput
from src.application.exceptions import EmailMessageNotFoundError, LeadNotFoundError
from src.application.use_cases.link_email_to_lead import LinkEmailToLeadUseCase
from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.enums import EmailDirection


# ── Фикстуры ───────────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc)


@pytest.fixture
def lead_id():
    return uuid4()


@pytest.fixture
def email_message(lead_id) -> EmailMessage:
    """Существующее письмо без привязки к лиду."""
    return EmailMessage.create_inbound(
        gmail_message_id="msg_100",
        gmail_thread_id="thr_100",
        from_address="client@example.com",
        to_addresses=["manager@crm.com"],
        subject="Вопрос",
        body="Текст письма",
        received_at=NOW,
    )


@pytest.fixture
def email_repo(email_message) -> AsyncMock:
    """Мок IEmailMessageRepository."""
    repo = AsyncMock()
    repo.get_by_id.return_value = email_message
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def lead_repo() -> AsyncMock:
    """Мок ILeadRepository."""
    repo = AsyncMock()
    # По умолчанию лид существует
    repo.get_by_id.return_value = object()
    return repo


@pytest.fixture
def use_case(email_repo, lead_repo) -> LinkEmailToLeadUseCase:
    return LinkEmailToLeadUseCase(
        email_repo=email_repo,
        lead_repo=lead_repo,
    )


@pytest.fixture
def valid_input(email_message, lead_id) -> LinkEmailToLeadInput:
    return LinkEmailToLeadInput(
        email_message_id=email_message.id,
        lead_id=lead_id,
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestLinkEmailToLeadHappyPath:
    async def test_returns_email_message_output(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput
    ) -> None:
        """execute возвращает EmailMessageOutput с привязанным lead_id."""
        result = await use_case.execute(valid_input)
        assert isinstance(result, EmailMessageOutput)
        assert result.lead_id == valid_input.lead_id

    async def test_save_called_after_link(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        email_repo: AsyncMock,
    ) -> None:
        """Репозиторий save() вызывается после привязки."""
        await use_case.execute(valid_input)
        email_repo.save.assert_called_once()

    async def test_email_repo_get_by_id_called(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        email_repo: AsyncMock,
    ) -> None:
        """Письмо загружается по ID."""
        await use_case.execute(valid_input)
        email_repo.get_by_id.assert_called_once_with(valid_input.email_message_id)


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestLinkEmailToLeadGuards:
    async def test_email_not_found_raises(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        email_repo: AsyncMock,
    ) -> None:
        """EmailMessageNotFoundError если письмо не найдено."""
        email_repo.get_by_id.return_value = None
        with pytest.raises(EmailMessageNotFoundError):
            await use_case.execute(valid_input)

    async def test_lead_not_found_raises(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        lead_repo: AsyncMock,
    ) -> None:
        """LeadNotFoundError если лид не найден."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(valid_input)

    async def test_email_already_linked_to_other_lead_raises(
        self, use_case: LinkEmailToLeadUseCase, email_message: EmailMessage,
        email_repo: AsyncMock,
    ) -> None:
        """ValueError если письмо уже привязано к другому лиду."""
        other_lead = uuid4()
        email_message.link_to_lead(other_lead)
        new_lead = uuid4()
        data = LinkEmailToLeadInput(
            email_message_id=email_message.id,
            lead_id=new_lead,
        )
        with pytest.raises(ValueError, match="уже привязано"):
            await use_case.execute(data)

    async def test_save_not_called_when_email_not_found(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        email_repo: AsyncMock,
    ) -> None:
        """Если письмо не найдено — save() не вызывается."""
        email_repo.get_by_id.return_value = None
        with pytest.raises(EmailMessageNotFoundError):
            await use_case.execute(valid_input)
        email_repo.save.assert_not_called()

    async def test_save_not_called_when_lead_not_found(
        self, use_case: LinkEmailToLeadUseCase, valid_input: LinkEmailToLeadInput,
        email_repo: AsyncMock, lead_repo: AsyncMock,
    ) -> None:
        """Если лид не найден — save() не вызывается."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(valid_input)
        email_repo.save.assert_not_called()
