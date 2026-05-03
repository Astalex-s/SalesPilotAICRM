import { type AnalyticsOverview, type DashboardAnalytics, type ManagersReport, type RevenueForecast } from '../types/analytics';
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

  getManagersReport: async (): Promise<ManagersReport> => {
    const { data } = await axiosInstance.get<ManagersReport>('/analytics/managers');
    return data;
  },

  exportCsv: async (): Promise<Blob> => {
    const { data } = await axiosInstance.get('/analytics/export/csv', {
      responseType: 'blob',
    });
    return data as Blob;
  },
};
