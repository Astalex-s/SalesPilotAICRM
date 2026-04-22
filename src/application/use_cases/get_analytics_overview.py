"""
GetAnalyticsOverviewUseCase — расширенная аналитика CRM.

Возвращает:
  - воронку конверсии лидов с процентами по каждому статусу
  - общий win rate и средний размер сделки
  - детальную статистику по каждой активной воронке продаж
"""
from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from src.application.dtos.analytics_dtos import (
    AnalyticsOverviewOutput,
    ConversionFunnelStep,
    PipelineStatsEntry,
)
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.value_objects.enums import DealStatus, LeadStatus

# Порядок отображения воронки лидов — от первого контакта к конверсии
_FUNNEL_ORDER: list[LeadStatus] = [
    LeadStatus.NEW,
    LeadStatus.CONTACTED,
    LeadStatus.QUALIFIED,
    LeadStatus.CONVERTED,
    LeadStatus.UNQUALIFIED,
]


class GetAnalyticsOverviewUseCase:
    """Агрегирует расширенную аналитику: воронку лидов и статистику воронок."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._pipeline_repo = pipeline_repo

    async def execute(self) -> AnalyticsOverviewOutput:
        """Загружает данные и формирует аналитический обзор."""
        leads = await self._lead_repo.find_all()
        deals = await self._deal_repo.find_all()
        pipelines = await self._pipeline_repo.find_active()

        # ── Воронка конверсии лидов ────────────────────────────────────────────
        total_leads = len(leads)
        lead_counts: dict[str, int] = defaultdict(int)
        for lead in leads:
            lead_counts[lead.status.value] += 1

        conversion_funnel = [
            ConversionFunnelStep(
                status=status.value,
                count=lead_counts.get(status.value, 0),
                percentage=round(
                    lead_counts.get(status.value, 0) / total_leads * 100.0, 1
                ) if total_leads > 0 else 0.0,
            )
            for status in _FUNNEL_ORDER
        ]

        converted_count = lead_counts.get(LeadStatus.CONVERTED.value, 0)
        conversion_rate = round(converted_count / total_leads * 100.0, 1) if total_leads > 0 else 0.0

        # ── Статистика сделок по воронкам ──────────────────────────────────────
        # Индексируем сделки по pipeline_id для O(n) группировки
        deals_by_pipeline: dict[UUID, list] = defaultdict(list)
        for deal in deals:
            deals_by_pipeline[deal.pipeline_id].append(deal)

        pipeline_stats: list[PipelineStatsEntry] = []
        for pipeline in pipelines:
            p_deals = deals_by_pipeline.get(pipeline.id, [])

            open_deals = [d for d in p_deals if d.status == DealStatus.OPEN]
            won_deals = [d for d in p_deals if d.status == DealStatus.WON]
            lost_deals = [d for d in p_deals if d.status == DealStatus.LOST]

            pipeline_value = sum(float(d.value.amount) for d in open_deals)
            won_revenue = sum(float(d.value.amount) for d in won_deals)

            decided = len(won_deals) + len(lost_deals)
            win_rate = round(len(won_deals) / decided * 100.0, 1) if decided > 0 else 0.0
            avg_deal_size = round(pipeline_value / len(open_deals), 2) if open_deals else 0.0

            pipeline_stats.append(
                PipelineStatsEntry(
                    pipeline_id=pipeline.id,
                    pipeline_name=pipeline.name,
                    total_deals=len(p_deals),
                    open_deals=len(open_deals),
                    won_deals=len(won_deals),
                    lost_deals=len(lost_deals),
                    pipeline_value=round(pipeline_value, 2),
                    won_revenue=round(won_revenue, 2),
                    win_rate=win_rate,
                    avg_deal_size=avg_deal_size,
                )
            )

        # ── Глобальные метрики сделок ──────────────────────────────────────────
        all_won = [d for d in deals if d.status == DealStatus.WON]
        all_lost = [d for d in deals if d.status == DealStatus.LOST]
        all_open = [d for d in deals if d.status == DealStatus.OPEN]

        total_decided = len(all_won) + len(all_lost)
        overall_win_rate = round(len(all_won) / total_decided * 100.0, 1) if total_decided > 0 else 0.0
        avg_deal_size = (
            round(sum(float(d.value.amount) for d in all_open) / len(all_open), 2)
            if all_open else 0.0
        )

        return AnalyticsOverviewOutput(
            total_leads=total_leads,
            conversion_rate=conversion_rate,
            conversion_funnel=conversion_funnel,
            total_deals=len(deals),
            overall_win_rate=overall_win_rate,
            avg_deal_size=avg_deal_size,
            pipeline_stats=pipeline_stats,
        )
