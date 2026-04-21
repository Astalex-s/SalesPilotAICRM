"""
Юнит-тесты GetNextBestActionUseCase.
Репозитории и AI-сервис заменены AsyncMock — зависимостей от I/O нет.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.ai_dtos import NextBestActionInput, NextBestActionOutput
from src.application.exceptions import DealNotFoundError, LeadNotFoundError
from src.application.ports.ai_service import NextBestAction
from src.application.use_cases.get_next_best_action import GetNextBestActionUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource
from src.domain.value_objects.money import Money


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_lead() -> Lead:
    return Lead.create(
        first_name="Анна",
        last_name="Смирнова",
        email=Email("anna@company.com"),
        owner_id=uuid4(),
        source=LeadSource.REFERRAL,
    )


@pytest.fixture
def sample_deal() -> Deal:
    return Deal.create(
        title="Интеграция CRM",
        owner_id=uuid4(),
        stage_id=uuid4(),
        pipeline_id=uuid4(),
        value=Money(amount=200_000, currency="RUB"),
    )


@pytest.fixture
def lead_repo(sample_lead: Lead) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = sample_lead
    return repo


@pytest.fixture
def deal_repo(sample_deal: Deal) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = sample_deal
    return repo


@pytest.fixture
def ai_service() -> AsyncMock:
    service = AsyncMock()
    service.next_best_action.return_value = NextBestAction(
        action="Назначить демо-встречу",
        priority="high",
        reasoning="Лид проявил интерес на прошлой неделе.",
    )
    return service


@pytest.fixture
def use_case(
    lead_repo: AsyncMock,
    deal_repo: AsyncMock,
    ai_service: AsyncMock,
) -> GetNextBestActionUseCase:
    return GetNextBestActionUseCase(
        lead_repo=lead_repo,
        deal_repo=deal_repo,
        ai_service=ai_service,
    )


# ── Успешный путь: entity_type="lead" ─────────────────────────────────────────

class TestNextBestActionLeadPath:
    async def test_returns_output_for_lead(
        self, use_case: GetNextBestActionUseCase, sample_lead: Lead
    ) -> None:
        """execute возвращает NextBestActionOutput для лида."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        result = await use_case.execute(data)
        assert isinstance(result, NextBestActionOutput)

    async def test_entity_id_and_type_match_for_lead(
        self, use_case: GetNextBestActionUseCase, sample_lead: Lead
    ) -> None:
        """entity_id и entity_type совпадают со входными данными."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        result = await use_case.execute(data)
        assert result.entity_id == sample_lead.id
        assert result.entity_type == "lead"

    async def test_action_and_priority_passed_for_lead(
        self, use_case: GetNextBestActionUseCase, sample_lead: Lead
    ) -> None:
        """Действие и приоритет из AI-сервиса передаются в DTO."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        result = await use_case.execute(data)
        assert result.action == "Назначить демо-встречу"
        assert result.priority == "high"

    async def test_lead_repo_called_for_lead_type(
        self,
        use_case: GetNextBestActionUseCase,
        sample_lead: Lead,
        lead_repo: AsyncMock,
    ) -> None:
        """При entity_type='lead' вызывается lead_repo.get_by_id."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        await use_case.execute(data)
        lead_repo.get_by_id.assert_called_once_with(sample_lead.id)

    async def test_deal_repo_not_called_for_lead(
        self,
        use_case: GetNextBestActionUseCase,
        sample_lead: Lead,
        deal_repo: AsyncMock,
    ) -> None:
        """При entity_type='lead' deal_repo не вызывается."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        await use_case.execute(data)
        deal_repo.get_by_id.assert_not_called()

    async def test_context_type_is_lead(
        self,
        use_case: GetNextBestActionUseCase,
        sample_lead: Lead,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит entity_type='lead'."""
        data = NextBestActionInput(entity_type="lead", entity_id=sample_lead.id)
        await use_case.execute(data)
        context = ai_service.next_best_action.call_args[0][0]
        assert context["entity_type"] == "lead"


# ── Успешный путь: entity_type="deal" ─────────────────────────────────────────

class TestNextBestActionDealPath:
    async def test_returns_output_for_deal(
        self, use_case: GetNextBestActionUseCase, sample_deal: Deal
    ) -> None:
        """execute возвращает NextBestActionOutput для сделки."""
        data = NextBestActionInput(entity_type="deal", entity_id=sample_deal.id)
        result = await use_case.execute(data)
        assert isinstance(result, NextBestActionOutput)

    async def test_entity_id_and_type_match_for_deal(
        self, use_case: GetNextBestActionUseCase, sample_deal: Deal
    ) -> None:
        """entity_id и entity_type совпадают для сделки."""
        data = NextBestActionInput(entity_type="deal", entity_id=sample_deal.id)
        result = await use_case.execute(data)
        assert result.entity_id == sample_deal.id
        assert result.entity_type == "deal"

    async def test_deal_repo_called_for_deal_type(
        self,
        use_case: GetNextBestActionUseCase,
        sample_deal: Deal,
        deal_repo: AsyncMock,
    ) -> None:
        """При entity_type='deal' вызывается deal_repo.get_by_id."""
        data = NextBestActionInput(entity_type="deal", entity_id=sample_deal.id)
        await use_case.execute(data)
        deal_repo.get_by_id.assert_called_once_with(sample_deal.id)

    async def test_lead_repo_not_called_for_deal(
        self,
        use_case: GetNextBestActionUseCase,
        sample_deal: Deal,
        lead_repo: AsyncMock,
    ) -> None:
        """При entity_type='deal' lead_repo не вызывается."""
        data = NextBestActionInput(entity_type="deal", entity_id=sample_deal.id)
        await use_case.execute(data)
        lead_repo.get_by_id.assert_not_called()

    async def test_context_type_is_deal(
        self,
        use_case: GetNextBestActionUseCase,
        sample_deal: Deal,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит entity_type='deal'."""
        data = NextBestActionInput(entity_type="deal", entity_id=sample_deal.id)
        await use_case.execute(data)
        context = ai_service.next_best_action.call_args[0][0]
        assert context["entity_type"] == "deal"


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestNextBestActionGuards:
    async def test_lead_not_found_raises(
        self, use_case: GetNextBestActionUseCase, lead_repo: AsyncMock
    ) -> None:
        """LeadNotFoundError если лид не найден."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(
                NextBestActionInput(entity_type="lead", entity_id=uuid4())
            )

    async def test_deal_not_found_raises(
        self, use_case: GetNextBestActionUseCase, deal_repo: AsyncMock
    ) -> None:
        """DealNotFoundError если сделка не найдена."""
        deal_repo.get_by_id.return_value = None
        with pytest.raises(DealNotFoundError):
            await use_case.execute(
                NextBestActionInput(entity_type="deal", entity_id=uuid4())
            )

    async def test_ai_not_called_when_lead_missing(
        self,
        use_case: GetNextBestActionUseCase,
        lead_repo: AsyncMock,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис не вызывается, если лид не найден."""
        lead_repo.get_by_id.return_value = None
        with pytest.raises(LeadNotFoundError):
            await use_case.execute(
                NextBestActionInput(entity_type="lead", entity_id=uuid4())
            )
        ai_service.next_best_action.assert_not_called()
