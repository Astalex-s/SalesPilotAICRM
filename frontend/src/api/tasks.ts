import { type CrmTask, type CreateTaskPayload, type TaskStatus, type UpdateTaskPayload } from '../types/task';
import axiosInstance from './axiosInstance';

interface ListTasksParams {
  assignee_id?: string;
  lead_id?: string;
  deal_id?: string;
  status?: TaskStatus;
  overdue_only?: boolean;
}

export const tasksApi = {
  list: async (params?: ListTasksParams): Promise<CrmTask[]> => {
    const { data } = await axiosInstance.get<CrmTask[]>('/tasks', { params });
    return data;
  },

  create: async (payload: CreateTaskPayload): Promise<CrmTask> => {
    const { data } = await axiosInstance.post<CrmTask>('/tasks', payload);
    return data;
  },

  update: async (taskId: string, payload: UpdateTaskPayload): Promise<CrmTask> => {
    const { data } = await axiosInstance.patch<CrmTask>(`/tasks/${taskId}`, payload);
    return data;
  },

  delete: async (taskId: string): Promise<void> => {
    await axiosInstance.delete(`/tasks/${taskId}`);
  },
};
