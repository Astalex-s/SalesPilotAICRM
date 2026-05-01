import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface AppSettings {
  notifEmail: boolean;
  notifDeal: boolean;
  notifLead: boolean;
  notifSystem: boolean;
  sidebarDefaultOpen: boolean;
}

interface SettingsState extends AppSettings {
  update: (patch: Partial<AppSettings>) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      notifEmail: true,
      notifDeal: true,
      notifLead: true,
      notifSystem: true,
      sidebarDefaultOpen: true,

      update: (patch) => set((s) => ({ ...s, ...patch })),
    }),
    { name: 'crm-settings' }
  )
);
