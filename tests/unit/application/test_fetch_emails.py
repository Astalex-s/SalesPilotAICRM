"""Юнит-тесты use case FetchEmailsUseCase.
Репозитории и IEmailService заменены AsyncMock — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from src.application.dtos.email_message_dtos import EmailMessageOutput, FetchEmailsInput
from src.application.exceptions import GmailNotAuthorizedError
from src.application.ports.email_service import FetchedEmail
from src.application.use_cases.fetch_emails import FetchEmailsUseCase
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import EmailDirection, LeadSource


# ── Фикстуры ───────────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc)


@pytest.fixture
def fetched_email_sample() -> FetchedEmail:
    """Образец письма, полученного из Gmail."""
    return FetchedEmail(
        gmail_message_id="gmail_001",
        thread_id="thr_001",
        from_address="client@example.com",
        to_addresses=["manager@crm.com"],
        subject="Запрос информации",
        body="Здравствуйте, пришлите прайс.",
        received_at=NOW,
    )


@pytest.fixture
def email_service(fetched_email_sample) -> AsyncMock:
    """Мок IEmailService."""
    svc = AsyncMock()
    svc.is_authorized.return_value = True
    svc.fetch_emails.return_value = [fetched_email_sample]
    return svc


@pytest.fixture
def email_repo() -> AsyncMock:
    """Мок IEmailMessageRepository."""
    repo = AsyncMock()
    # По умолчанию письмо не существует в БД
    repo.find_by_gmail_id.return_value = None
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def lead_repo() -> AsyncMock:
    """Мок ILeadRepository."""
    repo = AsyncMock()
    # По умолчанию лид не найден по email
    repo.find_by_email.return_value = None
    return repo


@pytest.fixture
def use_case(email_service, email_repo, lead_repo) -> FetchEmailsUseCase:
    return FetchEmailsUseCase(
        email_service=email_service,
        email_repo=email_repo,
        lead_repo=lead_repo,
    )


@pytest.fixture
def valid_input() -> FetchEmailsInput:
    return FetchEmailsInput(query="from:client@example.com", max_results=10)


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestFetchEmailsHappyPath:
    async def test_returns_list_of_outputs(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput
    ) -> None:
        """execute возвращает список EmailMessageOutput."""
        results = await use_case.execute(valid_input)
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], EmailMessageOutput)

    async def test_direction_is_inbound(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput
    ) -> None:
        """Загруженные письма имеют направление INBOUND."""
        results = await use_case.execute(valid_input)
        assert results[0].direction == EmailDirection.INBOUND

    async def test_gmail_ids_preserved(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput
    ) -> None:
        """Gmail-идентификаторы сохраняются в DTO."""
        results = await use_case.execute(valid_input)
        assert results[0].gmail_message_id == "gmail_001"
        assert results[0].gmail_thread_id == "thr_001"

    async def test_email_service_fetch_called(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput,
        email_service: AsyncMock,
    ) -> None:
        """IEmailService.fetch_emails вызывается с параметрами из input."""
        await use_case.execute(valid_input)
        email_service.fetch_emails.assert_called_once_with(
            query="from:client@example.com", max_results=10
        )


# ── Дедупликация ───────────────────────────────────────────────────────────────

class TestFetchEmailsDedup:
    async def test_existing_email_skipped(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput,
        email_repo: AsyncMock,
    ) -> None:
        """Если письмо уже в БД — оно пропускается."""
        email_repo.find_by_gmail_id.return_value = object()  # не None
        results = await use_case.execute(valid_input)
        assert results == []
        email_repo.save.assert_not_called()

    async def test_new_email_saved(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput,
        email_repo: AsyncMock,
    ) -> None:
        """Новое письмо сохраняется через репозиторий."""
        await use_case.execute(valid_input)
        email_repo.save.assert_called_once()


# ── Автопривязка к лиду ────────────────────────────────────────────────────────

class TestFetchEmailsAutoLink:
    async def test_auto_link_when_lead_found(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput,
        lead_repo: AsyncMock,
    ) -> None:
        """Если лид с таким email найден — письмо привязывается автоматически."""
        lead = Lead.create(
            first_name="Client",
            last_name="Example",
            email=Email("client@example.com"),
            owner_id=uuid4(),
            source=LeadSource.EMAIL_CAMPAIGN,
        )
        lead_repo.find_by_email.return_value = lead
        results = await use_case.execute(valid_input)
        assert results[0].lead_id == lead.id

    async def test_no_link_when_lead_not_found(
        self, use_case: FetchEmailsUseCase, valid_input: FetchEmailsInput,
    ) -> None:
        """Если лид не найден — lead_id остаётся None."""
        results = await use_case.execute(valid_input)
        assert results[0].lead_id is None


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestFetchEmailsGuards:
    async def test_gmail_not_authorized_raises(
        self, use_case: FetchEmailsUseCase, email_service: AsyncMock,
        valid_input: FetchEmailsInput,
    ) -> None:
        """GmailNotAuthorizedError если OAuth2-токены отсутствуют."""
        email_service.is_authorized.return_value = False
        with pytest.raises(GmailNotAuthorizedError):
            await use_case.execute(valid_input)

    async def test_gmail_not_authorized_does_not_fetch(
        self, use_case: FetchEmailsUseCase, email_service: AsyncMock,
        valid_input: FetchEmailsInput,
    ) -> None:
        """При отсутствии авторизации fetch_emails не вызывается."""
        email_service.is_authorized.return_value = False
        with pytest.raises(GmailNotAuthorizedError):
            await use_case.execute(valid_input)
        email_service.fetch_emails.assert_not_called()

    async def test_empty_result_from_provider(
        self, use_case: FetchEmailsUseCase, email_service: AsyncMock,
        valid_input: FetchEmailsInput,
    ) -> None:
        """Пустой список от провайдера → пустой список DTO."""
        email_service.fetch_emails.return_value = []
        results = await use_case.execute(valid_input)
        assert results == []
