"""
GetRevenueForecastUseCase — взвешенный прогноз выручки.

Возвращает:
  - закрытую выручку (WON-сделки)
  - суммарную стоимость активной воронки
  - взвешенный прогноз: Σ(value × stage.probability)
  - детализацию по каждой воронке
  - детализацию по каждому этапу
"""
from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from src.application.dtos.analytics_dtos import (
    PipelineForecastEntry,
    RevenueForecastOutput,
    StageForecastEntry,
)
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.value_objects.enums import DealStatus


class GetRevenueForecastUseCase:
    """Вычисляет детальный взвешенный прогноз выручки по воронкам и этапам."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._deal_repo = deal_repo
        self._pipeline_repo = pipeline_repo

    async def execute(self) -> RevenueForecastOutput:
        """Загружает сделки и воронки; строит прогноз по каждому срезу."""
        deals = await self._deal_repo.find_all()
        pipelines = await self._pipeline_repo.find_active()

        # ── Индексы для O(1)-доступа ───────────────────────────────────────────
        pipeline_map: dict[UUID, Pipeline] = {p.id: p for p in pipelines}
        stage_map: dict[UUID, tuple[Stage, Pipeline]] = {
            stage.id: (stage, pipeline)
            for pipeline in pipelines
            for stage in pipeline.stages
        }

        # ── Разделение сделок на OPEN и WON ───────────────────────────────────
        open_deals = [d for d in deals if d.status == DealStatus.OPEN]
        won_deals = [d for d in deals if d.status == DealStatus.WON]

        closed_revenue = round(sum(float(d.value.amount) for d in won_deals), 2)
        pipeline_value_total = round(sum(float(d.value.amount) for d in open_deals), 2)

        # ── Группировка OPEN-сделок по этапам ────────────────────────────────
        # stage_id → list[deal]
        deals_by_stage: dict[UUID, list] = defaultdict(list)
        for deal in open_deals:
            deals_by_stage[deal.stage_id].append(deal)

        # ── Группировка OPEN-сделок по воронкам ──────────────────────────────
        # pipeline_id → list[deal]
        deals_by_pipeline: dict[UUID, list] = defaultdict(list)
        won_by_pipeline: dict[UUID, list] = defaultdict(list)
        for deal in open_deals:
            deals_by_pipeline[deal.pipeline_id].append(deal)
        for deal in won_deals:
            won_by_pipeline[deal.pipeline_id].append(deal)

        # ── Прогноз по этапам ─────────────────────────────────────────────────
        by_stage: list[StageForecastEntry] = []
        total_weighted = 0.0

        for stage_id, stage_deals in deals_by_stage.items():
            lookup = stage_map.get(stage_id)
            if lookup is None:
                # Сделка на этапе удалённой воронки — пропускаем
                continue
            stage, pipeline = lookup

            total_val = sum(float(d.value.amount) for d in stage_deals)
            weighted = total_val * stage.probability
            total_weighted += weighted

            by_stage.append(
                StageForecastEntry(
                    stage_id=stage.id,
                    stage_name=stage.name,
                    pipeline_id=pipeline.id,
                    pipeline_name=pipeline.name,
                    probability=stage.probability,
                    deal_count=len(stage_deals),
                    total_value=round(total_val, 2),
                    weighted_forecast=round(weighted, 2),
                )
            )

        # Сортируем по убыванию прогноза для удобства чтения
        by_stage.sort(key=lambda e: e.weighted_forecast, reverse=True)

        # ── Прогноз по воронкам ───────────────────────────────────────────────
        by_pipeline: list[PipelineForecastEntry] = []

        for pipeline in pipelines:
            p_open = deals_by_pipeline.get(pipeline.id, [])
            p_won = won_by_pipeline.get(pipeline.id, [])

            p_value = sum(float(d.value.amount) for d in p_open)
            p_closed = sum(float(d.value.amount) for d in p_won)

            # Взвешенный прогноз: ищем вероятность по stage_map
            p_weighted = sum(
                float(d.value.amount) * stage_map[d.stage_id][0].probability
                for d in p_open
                if d.stage_id in stage_map
            )

            by_pipeline.append(
                PipelineForecastEntry(
                    pipeline_id=pipeline.id,
                    pipeline_name=pipeline.name,
                    open_deals=len(p_open),
                    pipeline_value=round(p_value, 2),
                    weighted_forecast=round(p_weighted, 2),
                    closed_revenue=round(p_closed, 2),
                )
            )

        by_pipeline.sort(key=lambda e: e.weighted_forecast, reverse=True)

        return RevenueForecastOutput(
            closed_revenue=closed_revenue,
            pipeline_value=pipeline_value_total,
            weighted_forecast=round(total_weighted, 2),
            by_pipeline=by_pipeline,
            by_stage=by_stage,
        )
