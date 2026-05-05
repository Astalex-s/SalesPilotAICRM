import { create } from 'zustand';
import { tasksApi } from '../api/tasks';
import { type CrmTask, type CreateTaskPayload, type UpdateTaskPayload } from '../types/task';

interface TaskState {
  tasks: CrmTask[];
  loading: boolean;
  error: string | null;

  fetchTasks: (params?: Parameters<typeof tasksApi.list>[0]) => Promise<void>;
  createTask: (payload: CreateTaskPayload) => Promise<CrmTask>;
  updateTask: (taskId: string, payload: UpdateTaskPayload) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async (params) => {
    set({ loading: true, error: null });
    try {
      const tasks = await tasksApi.list(params);
      set({ tasks, loading: false });
    } catch {
      set({ loading: false, error: 'Failed to load tasks' });
    }
  },

  createTask: async (payload) => {
    const task = await tasksApi.create(payload);
    set((s) => ({ tasks: [task, ...s.tasks] }));
    return task;
  },

  updateTask: async (taskId, payload) => {
    const updated = await tasksApi.update(taskId, payload);
    set((s) => ({ tasks: s.tasks.map((t) => (t.id === taskId ? updated : t)) }));
  },

  deleteTask: async (taskId) => {
    await tasksApi.delete(taskId);
    set((s) => ({ tasks: s.tasks.filter((t) => t.id !== taskId) }));
  },
}));
