"""
AnalyzeLostDealsUseCase — batch AI-анализ потерянных сделок.
Загружает все LOST-сделки, формирует контекст и делегирует AI-сервису.
"""
from __future__ import annotations

from src.application.dtos.ai_dtos import LostDealsAnalysisOutput
from src.application.ports.ai_service import IAIService
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.value_objects.enums import DealStatus


class AnalyzeLostDealsUseCase:
    """Batch-анализ проигранных сделок через AI."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        ai_service: IAIService,
    ) -> None:
        self._deal_repo = deal_repo
        self._ai_service = ai_service

    async def execute(self) -> LostDealsAnalysisOutput:
        """Загружает все LOST-сделки и возвращает AI-анализ паттернов потерь."""
        deals = await self._deal_repo.find_by_status(DealStatus.LOST)

        if not deals:
            return LostDealsAnalysisOutput(
                total_deals=0,
                total_lost_value=0.0,
                loss_patterns=[],
                recommendations=["Нет проигранных сделок для анализа."],
                summary="Проигранных сделок не найдено.",
            )

        deals_context = [
            {
                "title": d.title,
                "company": d.company or "—",
                "value_amount": float(d.value.amount),
                "value_currency": d.value.currency,
                "stage": str(d.stage_id),
                "closed_at": d.closed_at.strftime("%Y-%m-%d") if d.closed_at else "—",
                "created_at": d.created_at.strftime("%Y-%m-%d"),
            }
            for d in deals
        ]

        result = await self._ai_service.analyze_lost_deals(deals_context)

        return LostDealsAnalysisOutput(
            total_deals=result.total_deals,
            total_lost_value=result.total_lost_value,
            loss_patterns=result.loss_patterns,
            recommendations=result.recommendations,
            summary=result.summary,
        )
