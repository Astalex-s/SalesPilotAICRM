export type AiTone = 'formal' | 'friendly' | 'assertive';
export type ActionPriority = 'high' | 'medium' | 'low';

export interface LeadScore {
  lead_id: string;
  score: number;
  reasoning: string;
  recommended_actions: string[];
}

export interface NextBestAction {
  entity_id: string;
  entity_type: 'lead' | 'deal';
  action: string;
  priority: ActionPriority;
  reasoning: string;
}

export interface GeneratedEmail {
  lead_id: string;
  subject: string;
  body: string;
  tone: AiTone;
}

export interface DealForecast {
  deal_id: string;
  win_probability: number;
  risk_factors: string[];
  opportunities: string[];
}

export interface LostDealsAnalysis {
  total_deals: number;
  total_lost_value: number;
  loss_patterns: string[];
  recommendations: string[];
  summary: string;
}

export interface PipelineDigest {
  pipeline_id: string;
  pipeline_name: string;
  summary: string;
  key_metrics: string[];
  risks: string[];
  opportunities: string[];
  focus_deals: string[];
}
