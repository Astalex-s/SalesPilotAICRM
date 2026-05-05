import axiosInstance from './axiosInstance';
import { type CrmMeeting, type CreateMeetingPayload, type UpdateMeetingPayload } from '../types/meeting';

export const meetingsApi = {
  list: async (params?: {
    lead_id?: string;
    deal_id?: string;
    from_date?: string;
    to_date?: string;
    status?: string;
  }): Promise<CrmMeeting[]> => {
    const res = await axiosInstance.get<CrmMeeting[]>('/meetings', { params });
    return res.data;
  },

  create: async (payload: CreateMeetingPayload): Promise<CrmMeeting> => {
    const res = await axiosInstance.post<CrmMeeting>('/meetings', payload);
    return res.data;
  },

  update: async (meetingId: string, payload: UpdateMeetingPayload): Promise<CrmMeeting> => {
    const res = await axiosInstance.patch<CrmMeeting>(`/meetings/${meetingId}`, payload);
    return res.data;
  },

  delete: async (meetingId: string): Promise<void> => {
    await axiosInstance.delete(`/meetings/${meetingId}`);
  },
};
