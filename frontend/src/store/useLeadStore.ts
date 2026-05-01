import { create } from 'zustand';
import { leadsApi } from '../api/leads';
import { type CreateLeadPayload, type Lead, type UpdateLeadPayload } from '../types/lead';

interface LeadState {
  leads: Lead[];
  loading: boolean;
  error: string | null;
  fetchLeads: () => Promise<void>;
  createLead: (payload: CreateLeadPayload) => Promise<void>;
  updateLead: (leadId: string, payload: UpdateLeadPayload) => Promise<Lead>;
}

export const useLeadStore = create<LeadState>((set) => ({
  leads: [],
  loading: false,
  error: null,

  fetchLeads: async () => {
    set({ loading: true, error: null });
    try {
      const leads = await leadsApi.list();
      set({ leads, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  createLead: async (payload: CreateLeadPayload) => {
    set({ loading: true, error: null });
    try {
      const newLead = await leadsApi.create(payload);
      set((state) => ({ leads: [newLead, ...state.leads], loading: false }));
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  updateLead: async (leadId: string, payload: UpdateLeadPayload) => {
    const updated = await leadsApi.update(leadId, payload);
    set((state) => ({
      leads: state.leads.map((l) => (l.id === leadId ? updated : l)),
    }));
    return updated;
  },
}));
