"""
Юнит-тесты GenerateEmailUseCase.
Репозиторий и AI-сервис заменены AsyncMock — зависимостей от I/O нет.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.ai_dtos import GenerateEmailInput, GenerateEmailOutput
from src.application.exceptions import LeadNotFoundError
from src.application.ports.ai_service import EmailDraft
from src.application.use_cases.generate_email import GenerateEmailUseCase
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_lead() -> Lead:
    return Lead.create(
        first_name="Мария",
        last_name="Козлова",
        email=Email("maria@bizness.ru"),
        owner_id=uuid4(),
        source=LeadSource.COLD_CALL,
        company="Бизнес Плюс",
    )


@pytest.fixture
def lead_repo(sample_lead: Lead) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = sample_lead
    return repo


@pytest.fixture
def ai_service() -> AsyncMock:
    service = AsyncMock()
    service.generate_email.return_value = EmailDraft(
        subject="Предложение для Бизнес Плюс",
        body="Уважаемая Мария, хотим предложить вам...",
    )
    return service


@pytest.fixture
def use_case(lead_repo: AsyncMock, ai_service: AsyncMock) -> GenerateEmailUseCase:
    return GenerateEmailUseCase(lead_repo=lead_repo, ai_service=ai_service)


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestGenerateEmailHappyPath:
    async def test_returns_generate_email_output(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """execute возвращает GenerateEmailOutput при корректных данных."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id, tone="friendly")
        )
        assert isinstance(result, GenerateEmailOutput)

    async def test_output_lead_id_matches(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """lead_id в выходном DTO совпадает с входным."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id)
        )
        assert result.lead_id == sample_lead.id

    async def test_output_subject_from_ai(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """Тема письма передаётся из AI-сервиса в DTO."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id)
        )
        assert result.subject == "Предложение для Бизнес Плюс"

    async def test_output_body_from_ai(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """Тело письма передаётся из AI-сервиса в DTO."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id)
        )
        assert "Уважаемая Мария" in result.body

    async def test_output_tone_matches_input(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """Тон письма в DTO совпадает с входным значением."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id, tone="formal")
        )
        assert result.tone == "formal"

    async def test_default_tone_is_friendly(
        self, use_case: GenerateEmailUseCase, sample_lead: Lead
    ) -> None:
        """По умолчанию используется тон 'friendly'."""
        result = await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id)
        )
        assert result.tone == "friendly"

    async def test_ai_service_called_with_tone(
        self,
        use_case: GenerateEmailUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис вызывается с нужным тоном."""
        await use_case.execute(
            GenerateEmailInput(lead_id=sample_lead.id, tone="assertive")
        )
        _, kwargs = ai_service.generate_email.call_args
        assert kwargs["tone"] == "assertive"

    async def test_ai_service_called_with_extra_context(
        self,
        use_case: GenerateEmailUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис получает extra_context, если он передан."""
        await use_case.execute(
            GenerateEmailInput(
                lead_id=sample_lead.id,
                extra_context="Обсудили на конференции 15 апреля",
            )
        )
        _, kwargs = ai_service.generate_email.call_args
        assert kwargs["extra_context"] == "Обсудили на конференции 15 апреля"

    async def test_ai_service_called_with_none_extra_context(
        self,
        use_case: GenerateEmailUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """Если extra_context не передан, AI-сервис получает None."""
        await use_case.execute(GenerateEmailInput(lead_id=sample_lead.id))
        _, kwargs = ai_service.generate_email.call_args
        assert kwargs["extra_context"] is None

    async def test_lead_repo_called_with_id(
        self,
        use_case: GenerateEmailUseCase,
        sample_lead: Lead,
        lead_repo: AsyncMock,
    ) -> None:
        """Репозиторий get_by_id вызывается с правильным ID."""
        await use_case.execute(GenerateEmailInput(lead_id=sample_lead.id))
        lead_repo.get_by_id.assert_called_once_with(sample_lead.id)

    async def test_context_contains_first_name(
        self,
        use_case: GenerateEmailUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит first_name лида (для обращения)."""
        await use_case.execute(GenerateEmailInput(lead_id=sample_lead.id))
        context = ai_service.generate_email.call_args[1]["lead_context"]
        assert context["first_name"] == "Мария"


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestGenerateEmailGuards:
    async def test_lead_not_found_raises(
        self, use_case: GenerateEmailUseCase, lead_repo: AsyncMock
    ) -> None:
        """LeadNotFoundError при отсутствии лида в репозитории."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(GenerateEmailInput(lead_id=uuid4()))

    async def test_ai_not_called_when_lead_missing(
        self,
        use_case: GenerateEmailUseCase,
        lead_repo: AsyncMock,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис не вызывается, если лид не найден."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(GenerateEmailInput(lead_id=uuid4()))
        ai_service.generate_email.assert_not_called()
