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
