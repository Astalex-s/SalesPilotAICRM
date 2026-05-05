import { type Activity } from '../types/activity';
import { type ConvertLeadPayload, type Deal, type MoveDealStagePayload } from '../types/deal';
type CloseOutcome = 'won' | 'lost';
import axiosInstance from './axiosInstance';

interface ListDealsParams {
  pipeline_id?: string;
  stage_id?: string;
  owner_id?: string;
}

export const dealsApi = {
  list: async (params?: ListDealsParams): Promise<Deal[]> => {
    const { data } = await axiosInstance.get<Deal[]>('/deals', { params });
    return data;
  },

  create: async (payload: ConvertLeadPayload): Promise<Deal> => {
    const { data } = await axiosInstance.post<Deal>('/deals', payload);
    return data;
  },

  moveStage: async (dealId: string, payload: MoveDealStagePayload): Promise<Deal> => {
    const { data } = await axiosInstance.patch<Deal>(
      `/deals/${dealId}/stage`,
      payload,
    );
    return data;
  },

  close: async (dealId: string, outcome: CloseOutcome): Promise<Deal> => {
    const { data } = await axiosInstance.patch<Deal>(`/deals/${dealId}/close`, { outcome });
    return data;
  },

  getActivities: async (dealId: string): Promise<Activity[]> => {
    const { data } = await axiosInstance.get<Activity[]>(`/deals/${dealId}/activities`);
    return data;
  },

  addComment: async (dealId: string, body: string): Promise<Activity> => {
    const { data } = await axiosInstance.post<Activity>(`/deals/${dealId}/comments`, { body });
    return data;
  },
};
