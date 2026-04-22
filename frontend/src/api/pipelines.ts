import { type Pipeline } from '../types/pipeline';
import axiosInstance from './axiosInstance';

export const pipelinesApi = {
  get: async (pipelineId: string): Promise<Pipeline> => {
    const { data } = await axiosInstance.get<Pipeline>(`/pipelines/${pipelineId}`);
    return data;
  },
};
