"""
Роутер /api/v1/analytics — агрегированные метрики и прогнозы CRM.
Тонкие контроллеры: вызвать use case → вернуть DTO.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from fastapi.responses import StreamingResponse

from src.application.dtos.analytics_dtos import (
    AnalyticsOverviewOutput,
    DashboardAnalyticsOutput,
    ManagersReportOutput,
    RevenueForecastOutput,
)
from src.application.use_cases.get_analytics_overview import GetAnalyticsOverviewUseCase
from src.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from src.application.use_cases.get_managers_report import GetManagersReportUseCase
from src.application.use_cases.get_revenue_forecast import GetRevenueForecastUseCase
from src.interfaces.api.dependencies import (
    get_analytics_overview_use_case,
    get_dashboard_analytics_use_case,
    get_managers_report_use_case,
    get_revenue_forecast_use_case,
)
from src.interfaces.api.auth_dependencies import get_current_user
from src.application.dtos.auth_dtos import UserOutput

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get(
    "",
    response_model=AnalyticsOverviewOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Расширенная аналитика CRM",
    description=(
        "Возвращает полный аналитический обзор: "
        "воронку конверсии лидов с процентами по каждому статусу, "
        "общий win rate и средний размер сделки, "
        "детальную статистику по каждой активной воронке продаж."
    ),
)
async def get_analytics_overview(
    use_case: GetAnalyticsOverviewUseCase = Depends(get_analytics_overview_use_case),
) -> AnalyticsOverviewOutput:
    """GET /api/v1/analytics — расширенный аналитический обзор."""
    return await use_case.execute()


@router.get(
    "/forecast",
    response_model=RevenueForecastOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Прогноз выручки",
    description=(
        "Возвращает детальный взвешенный прогноз выручки: "
        "закрытую выручку (WON), стоимость активной воронки, "
        "взвешенный прогноз Σ(value × probability) "
        "с разбивкой по каждой воронке и каждому этапу."
    ),
)
async def get_revenue_forecast(
    use_case: GetRevenueForecastUseCase = Depends(get_revenue_forecast_use_case),
) -> RevenueForecastOutput:
    """GET /api/v1/analytics/forecast — взвешенный прогноз выручки."""
    return await use_case.execute()


@router.get(
    "/dashboard",
    response_model=DashboardAnalyticsOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Метрики дашборда",
    description=(
        "Возвращает агрегированные метрики CRM: "
        "общее количество лидов и сделок, стоимость воронки, "
        "взвешенный прогноз выручки, конверсию и распределение по статусам."
    ),
)
async def get_dashboard(
    use_case: GetDashboardAnalyticsUseCase = Depends(get_dashboard_analytics_use_case),
) -> DashboardAnalyticsOutput:
    """GET /api/v1/analytics/dashboard — метрики для главного дашборда."""
    return await use_case.execute()


@router.get(
    "/managers",
    response_model=ManagersReportOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Детальный отчёт по менеджерам",
    description=(
        "Возвращает аналитику по каждому менеджеру: лиды, конверсию, "
        "сделки (open/won/lost), win rate, выручку, avg deal size, просрочку. "
        "Отсортировано по won_revenue убыванием."
    ),
)
async def get_managers_report(
    use_case: GetManagersReportUseCase = Depends(get_managers_report_use_case),
) -> ManagersReportOutput:
    """GET /api/v1/analytics/managers — детальный отчёт по менеджерам."""
    return await use_case.execute()


@router.get(
    "/export/csv",
    status_code=http_status.HTTP_200_OK,
    summary="Экспорт аналитики в CSV",
    description=(
        "Возвращает полный аналитический отчёт в формате CSV: "
        "сводные метрики, воронка конверсии, разбивка по воронкам, "
        "прогноз выручки и детальный отчёт по менеджерам."
    ),
)
async def export_analytics_csv(
    overview_uc: GetAnalyticsOverviewUseCase = Depends(get_analytics_overview_use_case),
    forecast_uc: GetRevenueForecastUseCase = Depends(get_revenue_forecast_use_case),
    managers_uc: GetManagersReportUseCase = Depends(get_managers_report_use_case),
    _current_user: UserOutput = Depends(get_current_user),
) -> StreamingResponse:
    """GET /api/v1/analytics/export/csv — полный CSV-экспорт аналитики."""
    overview, forecast, managers_report = await _gather_analytics(
        overview_uc, forecast_uc, managers_uc
    )

    buf = io.StringIO()
    writer = csv.writer(buf)

    # ── Section 1: Overview ──────────────────────────────────────────────────
    writer.writerow(["# OVERVIEW"])
    writer.writerow(["Total Leads", "Conversion Rate %", "Total Deals", "Win Rate %", "Avg Deal Size $"])
    writer.writerow([
        overview.total_leads,
        round(overview.conversion_rate, 2),
        overview.total_deals,
        round(overview.overall_win_rate, 2),
        round(overview.avg_deal_size, 2),
    ])
    writer.writerow([])

    # ── Section 2: Conversion Funnel ────────────────────────────────────────
    writer.writerow(["# CONVERSION FUNNEL"])
    writer.writerow(["Status", "Count", "Percentage %"])
    for step in overview.conversion_funnel:
        writer.writerow([step.status, step.count, round(step.percentage, 2)])
    writer.writerow([])

    # ── Section 3: Pipeline Breakdown ───────────────────────────────────────
    writer.writerow(["# PIPELINE BREAKDOWN"])
    writer.writerow([
        "Pipeline", "Total Deals", "Open", "Won", "Lost",
        "Pipeline Value $", "Won Revenue $", "Win Rate %", "Avg Deal $",
    ])
    for p in overview.pipeline_stats:
        writer.writerow([
            p.pipeline_name,
            p.total_deals, p.open_deals, p.won_deals, p.lost_deals,
            round(p.pipeline_value, 2), round(p.won_revenue, 2),
            round(p.win_rate, 2), round(p.avg_deal_size, 2),
        ])
    writer.writerow([])

    # ── Section 4: Revenue Forecast ─────────────────────────────────────────
    writer.writerow(["# REVENUE FORECAST"])
    writer.writerow(["Closed Revenue $", "Pipeline Value $", "Weighted Forecast $"])
    writer.writerow([
        round(forecast.closed_revenue, 2),
        round(forecast.pipeline_value, 2),
        round(forecast.weighted_forecast, 2),
    ])
    writer.writerow([])
    writer.writerow(["Pipeline", "Open Deals", "Pipeline Value $", "Weighted Forecast $", "Closed Revenue $"])
    for pf in forecast.by_pipeline:
        writer.writerow([
            pf.pipeline_name, pf.open_deals,
            round(pf.pipeline_value, 2),
            round(pf.weighted_forecast, 2),
            round(pf.closed_revenue, 2),
        ])
    writer.writerow([])

    # ── Section 5: Managers Report ──────────────────────────────────────────
    writer.writerow(["# MANAGERS REPORT"])
    writer.writerow([
        "Manager", "Email",
        "Total Leads", "Converted Leads", "Conversion Rate %",
        "Total Deals", "Open", "Won", "Lost", "Win Rate %",
        "Won Revenue $", "Pipeline Value $", "Avg Deal $", "Overdue Deals",
    ])
    for m in managers_report.managers:
        writer.writerow([
            m.manager_name, m.manager_email,
            m.total_leads, m.converted_leads, round(m.conversion_rate, 2),
            m.total_deals, m.open_deals, m.won_deals, m.lost_deals,
            round(m.win_rate, 2),
            round(m.won_revenue, 2), round(m.pipeline_value, 2),
            round(m.avg_deal_size, 2), m.overdue_deals,
        ])

    buf.seek(0)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"analytics_{ts}.csv"

    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _gather_analytics(
    overview_uc: GetAnalyticsOverviewUseCase,
    forecast_uc: GetRevenueForecastUseCase,
    managers_uc: GetManagersReportUseCase,
) -> tuple[AnalyticsOverviewOutput, RevenueForecastOutput, ManagersReportOutput]:
    """Параллельно получает данные из трёх use case."""
    import asyncio
    overview, forecast, managers_report = await asyncio.gather(
        overview_uc.execute(),
        forecast_uc.execute(),
        managers_uc.execute(),
    )
    return overview, forecast, managers_report
