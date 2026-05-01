export type GdprEventType = 'user_data_deleted' | 'lead_anonymized';

export interface GdprAuditEntry {
  id: string;
  event_type: GdprEventType;
  target_type: string;
  target_id: string;
  summary: string;
  performed_at: string;
  performed_by_id: string | null;
}

export interface GdprAuditLog {
  entries: GdprAuditEntry[];
  total: number;
  limit: number;
  offset: number;
}

export interface DeleteUserDataResult {
  user_id: string;
  leads_deleted: number;
  emails_deleted: number;
  deals_deleted: number;
  activities_erased: number;
  audit_entry_id: string;
}

export interface AnonymizeLeadResult {
  lead_id: string;
  emails_deleted: number;
  activities_erased: number;
  audit_entry_id: string;
}
