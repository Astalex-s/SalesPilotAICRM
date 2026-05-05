export type TaskStatus = 'pending' | 'in_progress' | 'done' | 'cancelled';

export interface CrmTask {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  assignee_id: string;
  created_by_id: string;
  lead_id: string | null;
  deal_id: string | null;
  status: TaskStatus;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskPayload {
  title: string;
  description?: string | null;
  due_date?: string | null;
  assignee_id: string;
  lead_id?: string | null;
  deal_id?: string | null;
}

export interface UpdateTaskPayload {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  assignee_id?: string;
  status?: TaskStatus;
}
