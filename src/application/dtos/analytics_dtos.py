"""
DTO для аналитического модуля CRM.
Read-model: агрегированные метрики поверх лидов, сделок и воронок.
Нет зависимостей на ORM, FastAPI или конкретные провайдеры.
"""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class DealsStatusBreakdown(BaseModel):
    """Распределение сделок по статусам."""

    open: int = Field(ge=0)
    won: int = Field(ge=0)
    lost: int = Field(ge=0)


class LeadsStatusBreakdown(BaseModel):
    """Распределение лидов по статусам."""

    new: int = Field(ge=0)
    contacted: int = Field(ge=0)
    qualified: int = Field(ge=0)
    unqualified: int = Field(ge=0)
    converted: int = Field(ge=0)


# ── Overview DTOs ─────────────────────────────────────────────────────────────

class ConversionFunnelStep(BaseModel):
    """Один шаг воронки конверсии лидов."""

    status: str = Field(description="Статус лида")
    count: int = Field(ge=0, description="Количество лидов на этом шаге")
    percentage: float = Field(ge=0.0, le=100.0, description="Доля от общего числа лидов")


class PipelineStatsEntry(BaseModel):
    """Статистика по одной воронке продаж."""

    pipeline_id: UUID
    pipeline_name: str
    total_deals: int = Field(ge=0)
    open_deals: int = Field(ge=0)
    won_deals: int = Field(ge=0)
    lost_deals: int = Field(ge=0)
    pipeline_value: float = Field(ge=0.0, description="Сумма активных сделок (USD)")
    won_revenue: float = Field(ge=0.0, description="Выручка по закрытым выигранным сделкам (USD)")
    win_rate: float = Field(ge=0.0, le=100.0, description="Win rate: won / (won + lost) * 100")
    avg_deal_size: float = Field(ge=0.0, description="Средний размер активной сделки (USD)")


class AnalyticsOverviewOutput(BaseModel):
    """Расширенный обзор аналитики CRM."""

    # ── Лиды ──────────────────────────────────────────────────────────────────
    total_leads: int = Field(ge=0)
    conversion_rate: float = Field(ge=0.0, le=100.0)
    conversion_funnel: list[ConversionFunnelStep]

    # ── Сделки (суммарно) ─────────────────────────────────────────────────────
    total_deals: int = Field(ge=0)
    overall_win_rate: float = Field(ge=0.0, le=100.0, description="Win rate по всем воронкам")
    avg_deal_size: float = Field(ge=0.0, description="Средний размер активной сделки (USD)")

    # ── По воронкам ───────────────────────────────────────────────────────────
    pipeline_stats: list[PipelineStatsEntry]


# ── Forecast DTOs ──────────────────────────────────────────────────────────────

class StageForecastEntry(BaseModel):
    """Взвешенный прогноз выручки по одному этапу воронки."""

    stage_id: UUID
    stage_name: str
    pipeline_id: UUID
    pipeline_name: str
    probability: float = Field(ge=0.0, le=1.0)
    deal_count: int = Field(ge=0)
    total_value: float = Field(ge=0.0, description="Сумма активных сделок на этапе (USD)")
    weighted_forecast: float = Field(ge=0.0, description="total_value × probability (USD)")


class PipelineForecastEntry(BaseModel):
    """Взвешенный прогноз выручки по одной воронке."""

    pipeline_id: UUID
    pipeline_name: str
    open_deals: int = Field(ge=0)
    pipeline_value: float = Field(ge=0.0, description="Сумма активных сделок (USD)")
    weighted_forecast: float = Field(ge=0.0, description="Взвешенный прогноз (USD)")
    closed_revenue: float = Field(ge=0.0, description="Выручка по WON-сделкам (USD)")


class RevenueForecastOutput(BaseModel):
    """Детальный прогноз выручки по воронкам и этапам."""

    # ── Итоговые метрики ───────────────────────────────────────────────────────
    closed_revenue: float = Field(ge=0.0, description="Выручка по всем WON-сделкам (USD)")
    pipeline_value: float = Field(ge=0.0, description="Суммарная стоимость OPEN-сделок (USD)")
    weighted_forecast: float = Field(ge=0.0, description="Взвешенный прогноз по всем воронкам (USD)")

    # ── Детализация ───────────────────────────────────────────────────────────
    by_pipeline: list[PipelineForecastEntry]
    by_stage: list[StageForecastEntry]


# ── Manager Report DTOs ────────────────────────────────────────────────────────

class ManagerReportEntry(BaseModel):
    """Аналитика по одному менеджеру."""

    manager_id: UUID
    manager_name: str
    manager_email: str

    # Лиды
    total_leads: int = Field(ge=0)
    converted_leads: int = Field(ge=0)
    conversion_rate: float = Field(ge=0.0, le=100.0, description="converted / total_leads * 100")

    # Сделки
    total_deals: int = Field(ge=0)
    open_deals: int = Field(ge=0)
    won_deals: int = Field(ge=0)
    lost_deals: int = Field(ge=0)
    win_rate: float = Field(ge=0.0, le=100.0, description="won / (won + lost) * 100")

    # Финансы
    pipeline_value: float = Field(ge=0.0, description="Сумма активных сделок")
    won_revenue: float = Field(ge=0.0, description="Выручка по WON-сделкам")
    avg_deal_size: float = Field(ge=0.0, description="Средний размер активной сделки")

    # Риски
    overdue_deals: int = Field(ge=0, description="Просроченные открытые сделки")


class ManagersReportOutput(BaseModel):
    """Детальный отчёт по всем менеджерам."""

    managers: list[ManagerReportEntry]
    total_managers: int = Field(ge=0)


# ── Dashboard DTO (STEP 14) ───────────────────────────────────────────────────

class DashboardAnalyticsOutput(BaseModel):
    """Агрегированные метрики для главного дашборда CRM."""

    # ── Лиды ──────────────────────────────────────────────────────────────────
    total_leads: int = Field(ge=0, description="Всего лидов в системе")
    conversion_rate: float = Field(
        ge=0.0, le=100.0,
        description="Процент конвертации лидов: (converted / total) * 100",
    )
    leads_by_status: LeadsStatusBreakdown

    # ── Сделки ────────────────────────────────────────────────────────────────
    total_deals: int = Field(ge=0, description="Всего сделок в системе")
    open_deals: int = Field(ge=0, description="Активных сделок")
    pipeline_value: float = Field(
        ge=0.0,
        description="Суммарная стоимость активных сделок (USD)",
    )
    revenue_forecast: float = Field(
        ge=0.0,
        description="Взвешенный прогноз выручки (value × вероятность этапа, USD)",
    )
    deals_by_status: DealsStatusBreakdown
