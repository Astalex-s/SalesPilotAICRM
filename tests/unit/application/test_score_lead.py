"""
Юнит-тесты ScoreLeadUseCase.
Репозиторий и AI-сервис заменены AsyncMock — зависимостей от I/O нет.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.ai_dtos import LeadScoreInput, LeadScoreOutput
from src.application.exceptions import LeadNotFoundError
from src.application.ports.ai_service import LeadScore
from src.application.use_cases.score_lead import ScoreLeadUseCase
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource, LeadStatus


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_lead() -> Lead:
    """Готовый лид для подстановки в мок репозитория."""
    return Lead.create(
        first_name="Иван",
        last_name="Петров",
        email=Email("ivan@example.com"),
        owner_id=uuid4(),
        source=LeadSource.WEBSITE,
        company="Рога и Копыта",
    )


@pytest.fixture
def lead_repo(sample_lead: Lead) -> AsyncMock:
    """Мок репозитория — get_by_id возвращает sample_lead."""
    repo = AsyncMock()
    repo.get_by_id.return_value = sample_lead
    return repo


@pytest.fixture
def ai_service() -> AsyncMock:
    """Мок AI-сервиса — score_lead возвращает готовый результат."""
    service = AsyncMock()
    service.score_lead.return_value = LeadScore(
        score=0.75,
        reasoning="Высокий потенциал: крупная компания, активный интерес.",
        recommended_actions=["Позвонить сегодня", "Отправить КП"],
    )
    return service


@pytest.fixture
def use_case(lead_repo: AsyncMock, ai_service: AsyncMock) -> ScoreLeadUseCase:
    return ScoreLeadUseCase(lead_repo=lead_repo, ai_service=ai_service)


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestScoreLeadHappyPath:
    async def test_returns_lead_score_output(
        self, use_case: ScoreLeadUseCase, sample_lead: Lead
    ) -> None:
        """execute возвращает LeadScoreOutput при корректных данных."""
        result = await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        assert isinstance(result, LeadScoreOutput)

    async def test_output_lead_id_matches(
        self, use_case: ScoreLeadUseCase, sample_lead: Lead
    ) -> None:
        """lead_id в выходном DTO совпадает с входным."""
        result = await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        assert result.lead_id == sample_lead.id

    async def test_output_score_value(
        self, use_case: ScoreLeadUseCase, sample_lead: Lead
    ) -> None:
        """Оценка в DTO совпадает с тем, что вернул AI-сервис."""
        result = await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        assert result.score == 0.75

    async def test_output_reasoning_passed(
        self, use_case: ScoreLeadUseCase, sample_lead: Lead
    ) -> None:
        """Обоснование оценки передаётся из AI-сервиса в DTO."""
        result = await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        assert "Высокий потенциал" in result.reasoning

    async def test_output_recommended_actions(
        self, use_case: ScoreLeadUseCase, sample_lead: Lead
    ) -> None:
        """Список рекомендованных действий передаётся корректно."""
        result = await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        assert "Позвонить сегодня" in result.recommended_actions

    async def test_ai_service_called_with_context(
        self,
        use_case: ScoreLeadUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис вызывается ровно один раз с контекстом лида."""
        await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        ai_service.score_lead.assert_called_once()
        context = ai_service.score_lead.call_args[0][0]
        assert context["name"] == "Иван Петров"

    async def test_lead_repo_called_with_id(
        self,
        use_case: ScoreLeadUseCase,
        sample_lead: Lead,
        lead_repo: AsyncMock,
    ) -> None:
        """Репозиторий get_by_id вызывается с правильным ID."""
        await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        lead_repo.get_by_id.assert_called_once_with(sample_lead.id)

    async def test_context_contains_email(
        self,
        use_case: ScoreLeadUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит e-mail лида."""
        await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        context = ai_service.score_lead.call_args[0][0]
        assert context["email"] == "ivan@example.com"

    async def test_context_contains_status(
        self,
        use_case: ScoreLeadUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит текущий статус лида."""
        await use_case.execute(LeadScoreInput(lead_id=sample_lead.id))
        context = ai_service.score_lead.call_args[0][0]
        assert context["status"] == LeadStatus.NEW.value


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestScoreLeadGuards:
    async def test_lead_not_found_raises(
        self, use_case: ScoreLeadUseCase, lead_repo: AsyncMock
    ) -> None:
        """LeadNotFoundError при отсутствии лида в репозитории."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(LeadScoreInput(lead_id=uuid4()))

    async def test_ai_not_called_when_lead_missing(
        self,
        use_case: ScoreLeadUseCase,
        lead_repo: AsyncMock,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис не вызывается, если лид не найден."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(LeadScoreInput(lead_id=uuid4()))
        ai_service.score_lead.assert_not_called()
