export type ActivityType =
  | 'call'
  | 'email'
  | 'meeting'
  | 'note'
  | 'status_change'
  | 'stage_change'
  | 'lead_converted';

export type EntityType = 'lead' | 'deal';

export interface Activity {
  id: string;
  entity_type: EntityType;
  entity_id: string;
  activity_type: ActivityType;
  performed_by_id: string;
  body: string;
  occurred_at: string;
}
