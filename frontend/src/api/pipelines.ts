import axiosInstance from './axiosInstance';
import { type Pipeline } from '../types/pipeline';

export interface AddStagePayload {
  name: string;
  probability?: number;
  color?: string | null;
}

export interface UpdateStagePayload {
  name?: string;
  probability?: number;
  color?: string | null;
  clear_color?: boolean;
}

export const pipelinesApi = {
  /** GET /pipelines — список активных воронок */
  list: async (): Promise<Pipeline[]> => {
    const { data } = await axiosInstance.get<Pipeline[]>('/pipelines');
    return data;
  },

  /** GET /pipelines/:id — воронка с этапами */
  get: async (pipelineId: string): Promise<Pipeline> => {
    const { data } = await axiosInstance.get<Pipeline>(`/pipelines/${pipelineId}`);
    return data;
  },

  /** POST /pipelines — создать воронку */
  create: async (name: string): Promise<Pipeline> => {
    const { data } = await axiosInstance.post<Pipeline>('/pipelines', { name });
    return data;
  },

  /** PATCH /pipelines/:id — переименовать */
  update: async (pipelineId: string, name: string): Promise<Pipeline> => {
    const { data } = await axiosInstance.patch<Pipeline>(`/pipelines/${pipelineId}`, { name });
    return data;
  },

  /** DELETE /pipelines/:id — удалить */
  delete: async (pipelineId: string): Promise<void> => {
    await axiosInstance.delete(`/pipelines/${pipelineId}`);
  },

  /** POST /pipelines/:id/stages — добавить этап */
  addStage: async (pipelineId: string, payload: AddStagePayload): Promise<Pipeline> => {
    const { data } = await axiosInstance.post<Pipeline>(
      `/pipelines/${pipelineId}/stages`,
      payload,
    );
    return data;
  },

  /** PATCH /pipelines/:id/stages/:sid — обновить этап */
  updateStage: async (
    pipelineId: string,
    stageId: string,
    payload: UpdateStagePayload,
  ): Promise<Pipeline> => {
    const { data } = await axiosInstance.patch<Pipeline>(
      `/pipelines/${pipelineId}/stages/${stageId}`,
      payload,
    );
    return data;
  },

  /** DELETE /pipelines/:id/stages/:sid — удалить этап, возвращает обновлённую воронку */
  deleteStage: async (pipelineId: string, stageId: string): Promise<Pipeline> => {
    const { data } = await axiosInstance.delete<Pipeline>(
      `/pipelines/${pipelineId}/stages/${stageId}`,
    );
    return data;
  },
};
