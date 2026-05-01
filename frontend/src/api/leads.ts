import { type Activity } from '../types/activity';
import { type CreateLeadPayload, type Lead, type LeadStatus, type UpdateLeadPayload } from '../types/lead';
import axiosInstance from './axiosInstance';

interface ListLeadsParams {
  owner_id?: string;
  lead_status?: LeadStatus;
}

export const leadsApi = {
  list: async (params?: ListLeadsParams): Promise<Lead[]> => {
    const { data } = await axiosInstance.get<Lead[]>('/leads', { params });
    return data;
  },

  getById: async (leadId: string): Promise<Lead> => {
    const { data } = await axiosInstance.get<Lead>(`/leads/${leadId}`);
    return data;
  },

  getActivities: async (leadId: string): Promise<Activity[]> => {
    const { data } = await axiosInstance.get<Activity[]>(
      `/leads/${leadId}/activities`,
    );
    return data;
  },

  create: async (payload: CreateLeadPayload): Promise<Lead> => {
    const { data } = await axiosInstance.post<Lead>('/leads', payload);
    return data;
  },

  update: async (leadId: string, payload: UpdateLeadPayload): Promise<Lead> => {
    const { data } = await axiosInstance.patch<Lead>(`/leads/${leadId}`, payload);
    return data;
  },
};
