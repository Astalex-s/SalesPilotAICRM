import { type AnalyticsOverview, type DashboardAnalytics, type RevenueForecast } from '../types/analytics';
import axiosInstance from './axiosInstance';

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardAnalytics> => {
    const { data } = await axiosInstance.get<DashboardAnalytics>('/analytics/dashboard');
    return data;
  },

  getOverview: async (): Promise<AnalyticsOverview> => {
    const { data } = await axiosInstance.get<AnalyticsOverview>('/analytics');
    return data;
  },

  getForecast: async (): Promise<RevenueForecast> => {
    const { data } = await axiosInstance.get<RevenueForecast>('/analytics/forecast');
    return data;
  },
};
