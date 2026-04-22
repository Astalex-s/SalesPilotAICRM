import { type Deal, type MoveDealStagePayload } from '../types/deal';
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

  moveStage: async (dealId: string, payload: MoveDealStagePayload): Promise<Deal> => {
    const { data } = await axiosInstance.patch<Deal>(
      `/deals/${dealId}/stage`,
      payload,
    );
    return data;
  },
};
