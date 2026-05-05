import { create } from 'zustand';
import { meetingsApi } from '../api/meetings';
import { type CrmMeeting, type CreateMeetingPayload, type UpdateMeetingPayload } from '../types/meeting';

interface MeetingState {
  meetings: CrmMeeting[];
  loading: boolean;
  error: string | null;

  fetchMeetings: (params?: Parameters<typeof meetingsApi.list>[0]) => Promise<void>;
  createMeeting: (payload: CreateMeetingPayload) => Promise<CrmMeeting>;
  updateMeeting: (meetingId: string, payload: UpdateMeetingPayload) => Promise<void>;
  deleteMeeting: (meetingId: string) => Promise<void>;
}

export const useMeetingStore = create<MeetingState>((set) => ({
  meetings: [],
  loading: false,
  error: null,

  fetchMeetings: async (params) => {
    set({ loading: true, error: null });
    try {
      const meetings = await meetingsApi.list(params);
      set({ meetings, loading: false });
    } catch {
      set({ loading: false, error: 'Failed to load meetings' });
    }
  },

  createMeeting: async (payload) => {
    const meeting = await meetingsApi.create(payload);
    set((s) => ({ meetings: [...s.meetings, meeting].sort(
      (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    )}));
    return meeting;
  },

  updateMeeting: async (meetingId, payload) => {
    const updated = await meetingsApi.update(meetingId, payload);
    set((s) => ({ meetings: s.meetings.map((m) => (m.id === meetingId ? updated : m)) }));
  },

  deleteMeeting: async (meetingId) => {
    await meetingsApi.delete(meetingId);
    set((s) => ({ meetings: s.meetings.filter((m) => m.id !== meetingId) }));
  },
}));
