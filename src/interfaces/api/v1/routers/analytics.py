"""
Роутер /api/v1/analytics — агрегированные метрики и прогнозы CRM.
Тонкие контроллеры: вызвать use case → вернуть DTO.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.analytics_dtos import (
    AnalyticsOverviewOutput,
    DashboardAnalyticsOutput,
    RevenueForecastOutput,
)
from src.application.use_cases.get_analytics_overview import GetAnalyticsOverviewUseCase
from src.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from src.application.use_cases.get_revenue_forecast import GetRevenueForecastUseCase
from src.interfaces.api.dependencies import (
    get_analytics_overview_use_case,
    get_dashboard_analytics_use_case,
    get_revenue_forecast_use_case,
)

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
