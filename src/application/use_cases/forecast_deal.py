"""
ForecastDealUseCase — AI-прогноз вероятности закрытия сделки.

Единственная ответственность: загрузить сделку, сериализовать контекст,
вызвать IAIService.forecast_deal() и вернуть DTO.
"""
from __future__ import annotations

from src.application.dtos.ai_dtos import DealForecastInput, DealForecastOutput
from src.application.exceptions import DealNotFoundError
from src.application.ports.ai_service import IAIService
from src.domain.repositories.deal_repository import IDealRepository


class ForecastDealUseCase:
    """Запрашивает у AI-сервиса прогноз вероятности закрытия сделки."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        ai_service: IAIService,
    ) -> None:
        self._deal_repo = deal_repo
        self._ai_service = ai_service

    async def execute(self, data: DealForecastInput) -> DealForecastOutput:
        """Выполняет AI-прогноз по сделке.

        Последовательность:
        1. Загружает сделку — DealNotFoundError если не найдена.
        2. Сериализует доменные данные в словарь (граница AI).
        3. Вызывает IAIService.forecast_deal().
        4. Возвращает DealForecastOutput.
        """
        # Шаг 1: загрузка доменной сущности
        deal = await self._deal_repo.get_by_id(data.deal_id)
        if deal is None:
            raise DealNotFoundError(data.deal_id)

        # Шаг 2: сериализация контекста
        deal_context = {
            "title": deal.title,
            "status": deal.status.value,
            "value_amount": str(deal.value.amount),
            "value_currency": deal.value.currency,
            "contact_name": deal.contact_name or "Не указан",
            "company": deal.company or "Не указана",
            "expected_close_date": (
                deal.expected_close_date.isoformat()
                if deal.expected_close_date else "Не задана"
            ),
            "created_at": deal.created_at.isoformat(),
        }

        # Шаг 3: вызов AI через абстракцию
        result = await self._ai_service.forecast_deal(deal_context)

        # Шаг 4: формирование DTO
        return DealForecastOutput(
            deal_id=deal.id,
            win_probability=result.win_probability,
            risk_factors=result.risk_factors,
            opportunities=result.opportunities,
        )
