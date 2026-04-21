"""Юнит-тесты use case SendEmailUseCase.
Репозитории и IEmailService заменены AsyncMock — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.email_message_dtos import EmailMessageOutput, SendEmailInput
from src.application.exceptions import GmailNotAuthorizedError, LeadNotFoundError
from src.application.use_cases.send_email import SendEmailUseCase
from src.application.ports.email_service import SentEmailResult
from src.domain.value_objects.enums import EmailDirection


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def email_service() -> AsyncMock:
    """Мок IEmailService."""
    svc = AsyncMock()
    svc.is_authorized.return_value = True
    svc.send_email.return_value = SentEmailResult(
        gmail_message_id="gmail_msg_001",
        thread_id="gmail_thr_001",
    )
    return svc


@pytest.fixture
def email_repo() -> AsyncMock:
    """Мок IEmailMessageRepository."""
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def lead_repo() -> AsyncMock:
    """Мок ILeadRepository."""
    repo = AsyncMock()
    # По умолчанию лид существует
    repo.get_by_id.return_value = object()  # не None
    return repo


@pytest.fixture
def activity_repo() -> AsyncMock:
    """Мок IActivityRepository."""
    return AsyncMock()


@pytest.fixture
def use_case(
    email_service, email_repo, lead_repo, activity_repo
) -> SendEmailUseCase:
    return SendEmailUseCase(
        email_service=email_service,
        email_repo=email_repo,
        lead_repo=lead_repo,
        activity_repo=activity_repo,
    )


@pytest.fixture
def valid_input() -> SendEmailInput:
    return SendEmailInput(
        to="client@example.com",
        subject="Коммерческое предложение",
        body="Здравствуйте, отправляем КП.",
        performed_by_id=uuid4(),
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestSendEmailHappyPath:
    async def test_returns_email_message_output(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput
    ) -> None:
        """execute возвращает EmailMessageOutput при корректных данных."""
        result = await use_case.execute(valid_input)
        assert isinstance(result, EmailMessageOutput)

    async def test_output_direction_is_outbound(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput
    ) -> None:
        """Отправленное письмо имеет направление OUTBOUND."""
        result = await use_case.execute(valid_input)
        assert result.direction == EmailDirection.OUTBOUND

    async def test_output_subject_matches(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput
    ) -> None:
        """Тема письма в DTO совпадает со входным значением."""
        result = await use_case.execute(valid_input)
        assert result.subject == "Коммерческое предложение"

    async def test_output_gmail_ids_from_service(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput
    ) -> None:
        """Gmail-идентификаторы берутся из результата IEmailService."""
        result = await use_case.execute(valid_input)
        assert result.gmail_message_id == "gmail_msg_001"
        assert result.gmail_thread_id == "gmail_thr_001"

    async def test_email_repo_save_called(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput,
        email_repo: AsyncMock,
    ) -> None:
        """Репозиторий email вызывается для сохранения письма."""
        await use_case.execute(valid_input)
        email_repo.save.assert_called_once()

    async def test_email_service_send_called(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput,
        email_service: AsyncMock,
    ) -> None:
        """IEmailService.send_email вызывается с правильными аргументами."""
        await use_case.execute(valid_input)
        email_service.send_email.assert_called_once_with(
            to="client@example.com",
            subject="Коммерческое предложение",
            body="Здравствуйте, отправляем КП.",
            thread_id=None,
        )


# ── С привязкой к лиду ────────────────────────────────────────────────────────

class TestSendEmailWithLead:
    async def test_activity_logged_when_lead_id_set(
        self, use_case: SendEmailUseCase, lead_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        """Если lead_id указан — создаётся запись активности."""
        lead_id = uuid4()
        data = SendEmailInput(
            to="client@example.com",
            subject="Тема",
            body="Тело",
            lead_id=lead_id,
            performed_by_id=uuid4(),
        )
        await use_case.execute(data)
        activity_repo.save.assert_called_once()

    async def test_no_activity_when_no_lead_id(
        self, use_case: SendEmailUseCase, valid_input: SendEmailInput,
        activity_repo: AsyncMock,
    ) -> None:
        """Если lead_id не указан — активность не создаётся."""
        await use_case.execute(valid_input)
        activity_repo.save.assert_not_called()

    async def test_lead_not_found_raises(
        self, use_case: SendEmailUseCase, lead_repo: AsyncMock,
    ) -> None:
        """Если лид не найден — LeadNotFoundError."""
        lead_repo.get_by_id.return_value = None
        data = SendEmailInput(
            to="c@d.com",
            subject="Тема",
            body="Тело",
            lead_id=uuid4(),
            performed_by_id=uuid4(),
        )
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(data)


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestSendEmailGuards:
    async def test_gmail_not_authorized_raises(
        self, use_case: SendEmailUseCase, email_service: AsyncMock,
        valid_input: SendEmailInput,
    ) -> None:
        """GmailNotAuthorizedError если OAuth2-токены отсутствуют."""
        email_service.is_authorized.return_value = False
        with pytest.raises(GmailNotAuthorizedError):
            await use_case.execute(valid_input)

    async def test_gmail_not_authorized_does_not_send(
        self, use_case: SendEmailUseCase, email_service: AsyncMock,
        valid_input: SendEmailInput,
    ) -> None:
        """При отсутствии авторизации send_email не вызывается."""
        email_service.is_authorized.return_value = False
        with pytest.raises(GmailNotAuthorizedError):
            await use_case.execute(valid_input)
        email_service.send_email.assert_not_called()
