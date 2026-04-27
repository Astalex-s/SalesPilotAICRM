export type DealStatus = 'open' | 'won' | 'lost';
export type DealStage = 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';

export interface Deal {
  id: string;
  title: string;
  owner_id: string;
  stage_id: string;
  pipeline_id: string;
  value_amount: string;
  value_currency: string;
  status: DealStatus;
  contact_name: string | null;
  company: string | null;
  source_lead_id: string | null;
  expected_close_date: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MoveDealStagePayload {
  new_stage_id: string;
  pipeline_id: string;
  performed_by_id: string;
}
