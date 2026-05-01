import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type NotificationType = 'email' | 'deal' | 'lead' | 'system';

export interface CRMNotification {
  id: string;
  type: NotificationType;
  titleKey: string;
  msgKey: string;
  params?: Record<string, string>;
  read: boolean;
  timestamp: string; // ISO string
  link?: string;
}

interface NotificationState {
  notifications: CRMNotification[];
  seeded: boolean;
  add: (n: Omit<CRMNotification, 'id' | 'read'>) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  dismiss: (id: string) => void;
  seed: (items: Omit<CRMNotification, 'id' | 'read'>[]) => void;
}

function makeId(): string {
  return Math.random().toString(36).slice(2, 10);
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      notifications: [],
      seeded: false,

      add: (n) =>
        set((s) => ({
          notifications: [{ ...n, id: makeId(), read: false }, ...s.notifications],
        })),

      markRead: (id) =>
        set((s) => ({
          notifications: s.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),

      markAllRead: () =>
        set((s) => ({
          notifications: s.notifications.map((n) => ({ ...n, read: true })),
        })),

      dismiss: (id) =>
        set((s) => ({
          notifications: s.notifications.filter((n) => n.id !== id),
        })),

      seed: (items) =>
        set((s) => {
          if (s.seeded) return {};
          const seeded = items.map((n) => ({ ...n, id: makeId(), read: false }));
          return { notifications: seeded, seeded: true };
        }),
    }),
    { name: 'crm-notifications' }
  )
);

/* ── Seed data (called once on first app load) ─────────────────────────────── */
export const SEED_NOTIFICATIONS: Omit<CRMNotification, 'id' | 'read'>[] = [
  {
    type: 'system',
    titleKey: 'notifications.items.systemUpdate.title',
    msgKey: 'notifications.items.systemUpdate.msg',
    params: { message: 'SalesPilotAI v1.4.0 is now available — AI email generation improved.' },
    timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
  },
  {
    type: 'deal',
    titleKey: 'notifications.items.dealStageChanged.title',
    msgKey: 'notifications.items.dealStageChanged.msg',
    params: { deal: 'Acme Corp Enterprise', stage: 'Negotiation' },
    timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    link: '/deals',
  },
  {
    type: 'email',
    titleKey: 'notifications.items.emailReceived.title',
    msgKey: 'notifications.items.emailReceived.msg',
    params: { sender: 'john.doe@acme.com', subject: 'Re: Proposal for Q3' },
    timestamp: new Date(Date.now() - 1000 * 60 * 72).toISOString(),
    link: '/gmail',
  },
  {
    type: 'lead',
    titleKey: 'notifications.items.leadCreated.title',
    msgKey: 'notifications.items.leadCreated.msg',
    params: { name: 'Maria Petrova', company: 'GlobalTech LLC' },
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    link: '/leads',
  },
  {
    type: 'lead',
    titleKey: 'notifications.items.aiAnalysisReady.title',
    msgKey: 'notifications.items.aiAnalysisReady.msg',
    params: { name: 'James Wilson', score: '87' },
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    link: '/ai-assistant',
  },
];
