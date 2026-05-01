import { create } from 'zustand';
import { aiApi } from '../api/ai';
import { leadsApi } from '../api/leads';
import { type Activity } from '../types/activity';
import { type AiTone, type GeneratedEmail, type LeadScore, type NextBestAction } from '../types/ai';
import { type Lead, type UpdateLeadPayload } from '../types/lead';

interface AsyncSlice<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function pending<T>(): AsyncSlice<T> {
  return { data: null, loading: false, error: null };
}

interface LeadDetailState {
  lead: AsyncSlice<Lead>;
  activities: AsyncSlice<Activity[]>;
  score: AsyncSlice<LeadScore>;
  nextAction: AsyncSlice<NextBestAction>;
  generatedEmail: AsyncSlice<GeneratedEmail>;

  fetchLead: (leadId: string) => Promise<void>;
  fetchActivities: (leadId: string) => Promise<void>;
  fetchScore: (leadId: string) => Promise<void>;
  fetchNextAction: (leadId: string) => Promise<void>;
  generateEmail: (leadId: string, tone: AiTone, extraContext?: string) => Promise<void>;
  updateLead: (leadId: string, payload: UpdateLeadPayload) => Promise<void>;
  reset: () => void;
}

const initialState = {
  lead: pending<Lead>(),
  activities: pending<Activity[]>(),
  score: pending<LeadScore>(),
  nextAction: pending<NextBestAction>(),
  generatedEmail: pending<GeneratedEmail>(),
};

export const useLeadDetailStore = create<LeadDetailState>((set) => ({
  ...initialState,

  fetchLead: async (leadId) => {
    set((s) => ({ lead: { ...s.lead, loading: true, error: null } }));
    try {
      const data = await leadsApi.getById(leadId);
      set({ lead: { data, loading: false, error: null } });
    } catch (err) {
      set({ lead: { data: null, loading: false, error: (err as Error).message } });
    }
  },

  fetchActivities: async (leadId) => {
    set((s) => ({ activities: { ...s.activities, loading: true, error: null } }));
    try {
      const data = await leadsApi.getActivities(leadId);
      set({ activities: { data, loading: false, error: null } });
    } catch (err) {
      set({ activities: { data: null, loading: false, error: (err as Error).message } });
    }
  },

  fetchScore: async (leadId) => {
    set((s) => ({ score: { ...s.score, loading: true, error: null } }));
    try {
      const data = await aiApi.scoreLead(leadId);
      set({ score: { data, loading: false, error: null } });
    } catch (err) {
      set({ score: { data: null, loading: false, error: (err as Error).message } });
    }
  },

  fetchNextAction: async (leadId) => {
    set((s) => ({ nextAction: { ...s.nextAction, loading: true, error: null } }));
    try {
      const data = await aiApi.nextBestAction(leadId);
      set({ nextAction: { data, loading: false, error: null } });
    } catch (err) {
      set({ nextAction: { data: null, loading: false, error: (err as Error).message } });
    }
  },

  generateEmail: async (leadId, tone, extraContext) => {
    set((s) => ({ generatedEmail: { ...s.generatedEmail, loading: true, error: null } }));
    try {
      const data = await aiApi.generateEmail(leadId, tone, extraContext);
      set({ generatedEmail: { data, loading: false, error: null } });
    } catch (err) {
      set({ generatedEmail: { data: null, loading: false, error: (err as Error).message } });
    }
  },

  updateLead: async (leadId, payload) => {
    const updated = await leadsApi.update(leadId, payload);
    set({ lead: { data: updated, loading: false, error: null } });
  },

  reset: () => set(initialState),
}));
