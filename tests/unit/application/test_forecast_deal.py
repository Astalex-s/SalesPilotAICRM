"""
Юнит-тесты ForecastDealUseCase.
Репозиторий и AI-сервис заменены AsyncMock — зависимостей от I/O нет.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.ai_dtos import DealForecastInput, DealForecastOutput
from src.application.exceptions import DealNotFoundError
from src.application.ports.ai_service import DealForecast
from src.application.use_cases.forecast_deal import ForecastDealUseCase
from src.domain.entities.deal import Deal
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_deal() -> Deal:
    """Готовая сделка для подстановки в мок репозитория."""
    return Deal.create(
        title="Поставка ПО",
        owner_id=uuid4(),
        stage_id=uuid4(),
        pipeline_id=uuid4(),
        value=Money(amount=500_000, currency="RUB"),
        contact_name="Сергей Иванов",
        company="ТехКорп",
    )


@pytest.fixture
def deal_repo(sample_deal: Deal) -> AsyncMock:
    """Мок репозитория — get_by_id возвращает sample_deal."""
    repo = AsyncMock()
    repo.get_by_id.return_value = sample_deal
    return repo


@pytest.fixture
def ai_service() -> AsyncMock:
    """Мок AI-сервиса — forecast_deal возвращает готовый результат."""
    service = AsyncMock()
    service.forecast_deal.return_value = DealForecast(
        win_probability=0.82,
        risk_factors=["Затянутое согласование", "Конкуренты снижают цену"],
        opportunities=["Расширение до enterprise-лицензии"],
    )
    return service


@pytest.fixture
def use_case(deal_repo: AsyncMock, ai_service: AsyncMock) -> ForecastDealUseCase:
    return ForecastDealUseCase(deal_repo=deal_repo, ai_service=ai_service)


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestForecastDealHappyPath:
    async def test_returns_deal_forecast_output(
        self, use_case: ForecastDealUseCase, sample_deal: Deal
    ) -> None:
        """execute возвращает DealForecastOutput при корректных данных."""
        result = await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        assert isinstance(result, DealForecastOutput)

    async def test_output_deal_id_matches(
        self, use_case: ForecastDealUseCase, sample_deal: Deal
    ) -> None:
        """deal_id в выходном DTO совпадает с входным."""
        result = await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        assert result.deal_id == sample_deal.id

    async def test_output_win_probability(
        self, use_case: ForecastDealUseCase, sample_deal: Deal
    ) -> None:
        """win_probability в DTO совпадает с тем, что вернул AI-сервис."""
        result = await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        assert result.win_probability == 0.82

    async def test_output_risk_factors(
        self, use_case: ForecastDealUseCase, sample_deal: Deal
    ) -> None:
        """Список факторов риска передаётся корректно."""
        result = await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        assert "Затянутое согласование" in result.risk_factors

    async def test_output_opportunities(
        self, use_case: ForecastDealUseCase, sample_deal: Deal
    ) -> None:
        """Список возможностей передаётся корректно."""
        result = await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        assert "Расширение до enterprise-лицензии" in result.opportunities

    async def test_ai_service_called_once(
        self,
        use_case: ForecastDealUseCase,
        sample_deal: Deal,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис вызывается ровно один раз."""
        await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        ai_service.forecast_deal.assert_called_once()

    async def test_context_contains_title(
        self,
        use_case: ForecastDealUseCase,
        sample_deal: Deal,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит название сделки."""
        await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        context = ai_service.forecast_deal.call_args[0][0]
        assert context["title"] == "Поставка ПО"

    async def test_context_contains_status(
        self,
        use_case: ForecastDealUseCase,
        sample_deal: Deal,
        ai_service: AsyncMock,
    ) -> None:
        """Контекст для AI содержит статус сделки."""
        await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        context = ai_service.forecast_deal.call_args[0][0]
        assert context["status"] == DealStatus.OPEN.value

    async def test_deal_repo_called_with_id(
        self,
        use_case: ForecastDealUseCase,
        sample_deal: Deal,
        deal_repo: AsyncMock,
    ) -> None:
        """Репозиторий get_by_id вызывается с правильным ID."""
        await use_case.execute(DealForecastInput(deal_id=sample_deal.id))
        deal_repo.get_by_id.assert_called_once_with(sample_deal.id)


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestForecastDealGuards:
    async def test_deal_not_found_raises(
        self, use_case: ForecastDealUseCase, deal_repo: AsyncMock
    ) -> None:
        """DealNotFoundError при отсутствии сделки в репозитории."""
        deal_repo.get_by_id.return_value = None
        with pytest.raises(DealNotFoundError):
            await use_case.execute(DealForecastInput(deal_id=uuid4()))

    async def test_ai_not_called_when_deal_missing(
        self,
        use_case: ForecastDealUseCase,
        deal_repo: AsyncMock,
        ai_service: AsyncMock,
    ) -> None:
        """AI-сервис не вызывается, если сделка не найдена."""
        deal_repo.get_by_id.return_value = None
        with pytest.raises(DealNotFoundError):
            await use_case.execute(DealForecastInput(deal_id=uuid4()))
        ai_service.forecast_deal.assert_not_called()
