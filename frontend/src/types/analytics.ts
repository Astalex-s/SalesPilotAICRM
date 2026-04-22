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
