import { create } from 'zustand';
import { analyticsApi } from '../api/analytics';
import { type DashboardAnalytics } from '../types/analytics';

interface DashboardState {
  data: DashboardAnalytics | null;
  loading: boolean;
  error: string | null;
  fetchDashboard: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  data: null,
  loading: false,
  error: null,

  fetchDashboard: async () => {
    set({ loading: true, error: null });
    try {
      const data = await analyticsApi.getDashboard();
      set({ data, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },
}));
