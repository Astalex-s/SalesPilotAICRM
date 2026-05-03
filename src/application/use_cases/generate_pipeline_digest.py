"""
GeneratePipelineDigestUseCase — еженедельная AI-сводка по воронке продаж.
Агрегирует статистику воронки и делегирует AI-сервису формирование дайджеста.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.ai_dtos import PipelineDigestOutput
from src.application.exceptions import PipelineNotFoundError
from src.application.ports.ai_service import IAIService
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.value_objects.enums import DealStatus


class GeneratePipelineDigestUseCase:
    """Генерирует еженедельный AI-дайджест для указанной воронки."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        pipeline_repo: IPipelineRepository,
        ai_service: IAIService,
    ) -> None:
        self._deal_repo = deal_repo
        self._pipeline_repo = pipeline_repo
        self._ai_service = ai_service

    async def execute(self, pipeline_id: UUID) -> PipelineDigestOutput:
        """Собирает статистику воронки и возвращает AI-дайджест."""
        pipeline = await self._pipeline_repo.get_by_id(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(pipeline_id)

        all_deals = await self._deal_repo.find_by_pipeline(pipeline_id)

        open_deals = [d for d in all_deals if d.status == DealStatus.OPEN]
        won_deals  = [d for d in all_deals if d.status == DealStatus.WON]
        lost_deals = [d for d in all_deals if d.status == DealStatus.LOST]

        open_value = sum(float(d.value.amount) for d in open_deals)
        won_value  = sum(float(d.value.amount) for d in won_deals)
        currency   = all_deals[0].value.currency if all_deals else "USD"

        total_closed = len(won_deals) + len(lost_deals)
        win_rate = (len(won_deals) / total_closed * 100) if total_closed > 0 else 0.0

        avg_deal_value = (open_value / len(open_deals)) if open_deals else 0.0

        # Распределение по этапам
        stage_counts: dict[str, int] = {}
        for deal in open_deals:
            key = str(deal.stage_id)
            stage_counts[key] = stage_counts.get(key, 0) + 1
        stages_summary = "; ".join(
            f"Этап {sid[:8]}: {cnt} сд." for sid, cnt in stage_counts.items()
        ) or "—"

        # Застрявшие сделки (без изменений более 14 дней)
        from datetime import datetime, timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        stale = [d for d in open_deals if d.updated_at < cutoff]
        stale_deals = (
            "; ".join(d.title for d in stale[:5]) + ("..." if len(stale) > 5 else "")
            if stale else "нет"
        )

        pipeline_context = {
            "pipeline_name": pipeline.name,
            "total_deals": len(all_deals),
            "open_deals": len(open_deals),
            "won_deals": len(won_deals),
            "lost_deals": len(lost_deals),
            "open_value": open_value,
            "won_value": won_value,
            "currency": currency,
            "win_rate": win_rate,
            "avg_deal_value": avg_deal_value,
            "stages_summary": stages_summary,
            "stale_deals": stale_deals,
        }

        result = await self._ai_service.generate_pipeline_digest(pipeline_context)

        return PipelineDigestOutput(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline.name,
            summary=result.summary,
            key_metrics=result.key_metrics,
            risks=result.risks,
            opportunities=result.opportunities,
            focus_deals=result.focus_deals,
        )
