export interface DealsStatusBreakdown {
  open: number;
  won: number;
  lost: number;
}

export interface LeadsStatusBreakdown {
  new: number;
  contacted: number;
  qualified: number;
  unqualified: number;
  converted: number;
}

export interface DashboardAnalytics {
  total_leads: number;
  conversion_rate: number;
  leads_by_status: LeadsStatusBreakdown;
  total_deals: number;
  open_deals: number;
  pipeline_value: number;
  revenue_forecast: number;
  deals_by_status: DealsStatusBreakdown;
}

// ── Analytics Overview ────────────────────────────────────────────────────────

export interface ConversionFunnelStep {
  status: string;
  count: number;
  percentage: number;
}

export interface PipelineStatsEntry {
  pipeline_id: string;
  pipeline_name: string;
  total_deals: number;
  open_deals: number;
  won_deals: number;
  lost_deals: number;
  pipeline_value: number;
  won_revenue: number;
  win_rate: number;
  avg_deal_size: number;
}

export interface AnalyticsOverview {
  total_leads: number;
  conversion_rate: number;
  conversion_funnel: ConversionFunnelStep[];
  total_deals: number;
  overall_win_rate: number;
  avg_deal_size: number;
  pipeline_stats: PipelineStatsEntry[];
}

// ── Managers Report ───────────────────────────────────────────────────────────

export interface ManagerReportEntry {
  manager_id: string;
  manager_name: string;
  manager_email: string;
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
  total_deals: number;
  open_deals: number;
  won_deals: number;
  lost_deals: number;
  win_rate: number;
  pipeline_value: number;
  won_revenue: number;
  avg_deal_size: number;
  overdue_deals: number;
}

export interface ManagersReport {
  managers: ManagerReportEntry[];
  total_managers: number;
}

// ── Revenue Forecast ──────────────────────────────────────────────────────────

export interface PipelineForecastEntry {
  pipeline_id: string;
  pipeline_name: string;
  open_deals: number;
  pipeline_value: number;
  weighted_forecast: number;
  closed_revenue: number;
}

export interface RevenueForecast {
  closed_revenue: number;
  pipeline_value: number;
  weighted_forecast: number;
  by_pipeline: PipelineForecastEntry[];
}
