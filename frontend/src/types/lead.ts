export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'unqualified' | 'converted';
export type LeadSource =
  | 'website'
  | 'referral'
  | 'cold_call'
  | 'social_media'
  | 'email_campaign'
  | 'other';

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  company: string | null;
  status: LeadStatus;
  source: LeadSource;
  notes: string | null;
  owner_id: string;
  converted_deal_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateLeadPayload {
  status?: LeadStatus;
  notes?: string;
}

export interface CreateLeadPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  source?: LeadSource;
  owner_id: string;
}
