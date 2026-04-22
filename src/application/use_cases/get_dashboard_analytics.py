"""
GetDashboardAnalyticsUseCase — агрегирует метрики для главного дашборда.

Единственная ответственность: загрузить данные из репозиториев,
вычислить производные метрики, вернуть единый DTO.
Никакой бизнес-логики изменения состояния — только чтение.
"""
from __future__ import annotations

from collections import Counter
from uuid import UUID

from src.application.dtos.analytics_dtos import (
    DashboardAnalyticsOutput,
    DealsStatusBreakdown,
    LeadsStatusBreakdown,
)
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.value_objects.enums import DealStatus, LeadStatus


class GetDashboardAnalyticsUseCase:
    """Возвращает агрегированные метрики CRM-дашборда."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._pipeline_repo = pipeline_repo

    async def execute(self) -> DashboardAnalyticsOutput:
        """Параллельно загружает лиды, сделки и воронки; вычисляет метрики."""
        # ── Загрузка данных ────────────────────────────────────────────────────
        leads = await self._lead_repo.find_all()
        deals = await self._deal_repo.find_all()
        pipelines = await self._pipeline_repo.find_active()

        # ── Карта вероятностей: stage_id → probability ─────────────────────────
        stage_probability: dict[UUID, float] = {
            stage.id: stage.probability
            for pipeline in pipelines
            for stage in pipeline.stages
        }

        # ── Метрики лидов ──────────────────────────────────────────────────────
        total_leads = len(leads)
        lead_status_counts: Counter[str] = Counter(lead.status.value for lead in leads)

        converted_count = lead_status_counts.get(LeadStatus.CONVERTED.value, 0)
        conversion_rate = (converted_count / total_leads * 100.0) if total_leads > 0 else 0.0

        leads_by_status = LeadsStatusBreakdown(
            new=lead_status_counts.get(LeadStatus.NEW.value, 0),
            contacted=lead_status_counts.get(LeadStatus.CONTACTED.value, 0),
            qualified=lead_status_counts.get(LeadStatus.QUALIFIED.value, 0),
            unqualified=lead_status_counts.get(LeadStatus.UNQUALIFIED.value, 0),
            converted=converted_count,
        )

        # ── Метрики сделок ─────────────────────────────────────────────────────
        total_deals = len(deals)
        deal_status_counts: Counter[str] = Counter(deal.status.value for deal in deals)

        open_deals_list = [d for d in deals if d.status == DealStatus.OPEN]
        open_deals = len(open_deals_list)

        pipeline_value = sum(float(d.value.amount) for d in open_deals_list)

        revenue_forecast = sum(
            float(d.value.amount) * stage_probability.get(d.stage_id, 0.5)
            for d in open_deals_list
        )

        deals_by_status = DealsStatusBreakdown(
            open=deal_status_counts.get(DealStatus.OPEN.value, 0),
            won=deal_status_counts.get(DealStatus.WON.value, 0),
            lost=deal_status_counts.get(DealStatus.LOST.value, 0),
        )

        return DashboardAnalyticsOutput(
            total_leads=total_leads,
            conversion_rate=round(conversion_rate, 1),
            leads_by_status=leads_by_status,
            total_deals=total_deals,
            open_deals=open_deals,
            pipeline_value=round(pipeline_value, 2),
            revenue_forecast=round(revenue_forecast, 2),
            deals_by_status=deals_by_status,
        )
