export interface Stage {
  id: string;
  pipeline_id: string;
  name: string;
  order: number;
  probability: number;
}

export interface Pipeline {
  id: string;
  name: string;
  owner_id: string;
  stages: Stage[];
  is_active: boolean;
  created_at: string;
}
