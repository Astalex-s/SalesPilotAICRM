export type MeetingStatus = 'scheduled' | 'completed' | 'cancelled';

export interface CrmMeeting {
  id: string;
  title: string;
  description: string | null;
  start_time: string;   // ISO datetime
  end_time: string | null;
  location: string | null;
  lead_id: string | null;
  deal_id: string | null;
  created_by_id: string;
  status: MeetingStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateMeetingPayload {
  title: string;
  description?: string | null;
  start_time: string;
  end_time?: string | null;
  location?: string | null;
  lead_id?: string | null;
  deal_id?: string | null;
}

export interface UpdateMeetingPayload {
  meeting_id?: string;
  title?: string;
  description?: string | null;
  start_time?: string;
  end_time?: string | null;
  location?: string | null;
  status?: MeetingStatus;
}
