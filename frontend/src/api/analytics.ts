import { type DashboardAnalytics } from '../types/analytics';
import axiosInstance from './axiosInstance';

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardAnalytics> => {
    const { data } = await axiosInstance.get<DashboardAnalytics>('/analytics/dashboard');
    return data;
  },
};
