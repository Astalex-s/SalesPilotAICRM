import { create } from 'zustand';
import { dealsApi } from '../api/deals';
import { leadsApi } from '../api/leads';
import { pipelinesApi } from '../api/pipelines';
import { type Deal } from '../types/deal';
import { type Lead } from '../types/lead';
import { type Pipeline } from '../types/pipeline';

/** Columns indexed by stage_id → ordered list of deals. */
export type KanbanColumns = Record<string, Deal[]>;

interface KanbanState {
  pipeline: Pipeline | null;
  allPipelines: Pipeline[];
  columns: KanbanColumns;
  leadsPool: Lead[];
  loading: boolean;
  error: string | null;

  /** Load list of all active pipelines. */
  loadPipelines: () => Promise<void>;

  /** Load pipeline metadata + all its deals, build columns. */
  loadBoard: (pipelineId: string) => Promise<void>;

  /** Reload the currently open board (used after stage edits). */
  reloadBoard: () => Promise<void>;

  /** Load leads that have no deal (unassigned pool). */
  loadLeadsPool: () => Promise<void>;

  /** Add a single lead to the pool (after creating via AddLeadDialog). */
  addLeadToPool: (lead: Lead) => void;

  /** Reorder leads within the pool (visual only). */
  reorderLeadsPool: (fromIndex: number, toIndex: number) => void;

  /**
   * Promote a lead to a deal: qualify it + create deal in the target stage.
   * Optimistic remove from pool; reloads board on success; rolls back on error.
   */
  promoteLeadToDeal: (params: {
    leadId: string;
    stageId: string;
    pipelineId: string;
    performedById: string;
  }) => Promise<void>;

  /**
   * Move a deal from one stage column to another.
   * Applies optimistic update immediately; rolls back on API error.
   */
  moveDeal: (params: {
    dealId: string;
    fromStageId: string;
    toStageId: string;
    toIndex: number;
    pipelineId: string;
    performedById: string;
  }) => Promise<void>;
}

function buildColumns(pipeline: Pipeline, deals: Deal[]): KanbanColumns {
  const cols: KanbanColumns = {};
  for (const stage of pipeline.stages) {
    cols[stage.id] = [];
  }
  for (const deal of deals) {
    if (cols[deal.stage_id]) {
      cols[deal.stage_id].push(deal);
    }
  }
  return cols;
}

export const useKanbanStore = create<KanbanState>((set, get) => ({
  pipeline: null,
  allPipelines: [],
  columns: {},
  leadsPool: [],
  loading: false,
  error: null,

  loadPipelines: async () => {
    try {
      const pipelines = await pipelinesApi.list();
      set({ allPipelines: pipelines });
    } catch (_) {
      // non-critical — fail silently
    }
  },

  reloadBoard: async () => {
    const { pipeline } = get();
    if (pipeline) await get().loadBoard(pipeline.id);
  },

  loadBoard: async (pipelineId: string) => {
    set({ loading: true, error: null });
    try {
      const [pipeline, deals] = await Promise.all([
        pipelinesApi.get(pipelineId),
        dealsApi.list({ pipeline_id: pipelineId }),
      ]);
      set({ pipeline, columns: buildColumns(pipeline, deals), loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
    // Load leads pool alongside board (non-blocking)
    get().loadLeadsPool();
  },

  loadLeadsPool: async () => {
    try {
      const leads = await leadsApi.list();
      const pool = leads.filter(
        (l) => l.status !== 'converted' && l.converted_deal_id === null,
      );
      set({ leadsPool: pool });
    } catch (_) {
      // non-critical — fail silently
    }
  },

  addLeadToPool: (lead: Lead) => {
    set((state) => ({ leadsPool: [...state.leadsPool, lead] }));
  },

  reorderLeadsPool: (fromIndex: number, toIndex: number) => {
    const pool = [...get().leadsPool];
    const [moved] = pool.splice(fromIndex, 1);
    pool.splice(toIndex, 0, moved);
    set({ leadsPool: pool });
  },

  promoteLeadToDeal: async ({ leadId, stageId, pipelineId, performedById }) => {
    const { leadsPool } = get();
    const lead = leadsPool.find((l) => l.id === leadId);
    if (!lead) return;

    // Optimistic: remove from pool immediately
    set({ leadsPool: leadsPool.filter((l) => l.id !== leadId) });

    try {
      // Qualify lead if needed
      if (lead.status !== 'qualified') {
        await leadsApi.update(leadId, { status: 'qualified' });
      }
      // Create deal in target stage
      const dealTitle = `${lead.first_name} ${lead.last_name}${lead.company ? ` — ${lead.company}` : ''}`;
      await dealsApi.create({
        lead_id: leadId,
        stage_id: stageId,
        pipeline_id: pipelineId,
        deal_title: dealTitle,
        performed_by_id: performedById,
      });
      // Reload board to show the new deal
      await get().loadBoard(pipelineId);
    } catch (err) {
      // Rollback: put lead back in pool
      set({ leadsPool, error: (err as Error).message });
    }
  },

  moveDeal: async ({ dealId, fromStageId, toStageId, toIndex, pipelineId, performedById }) => {
    const { columns } = get();

    // ── Optimistic update ──────────────────────────────────────────────────────
    const sourceList = [...(columns[fromStageId] ?? [])];
    const destList = fromStageId === toStageId
      ? sourceList
      : [...(columns[toStageId] ?? [])];

    const dealIndex = sourceList.findIndex((d) => d.id === dealId);
    if (dealIndex === -1) return;

    const [movedDeal] = sourceList.splice(dealIndex, 1);
    const updatedDeal = { ...movedDeal, stage_id: toStageId };

    if (fromStageId === toStageId) {
      sourceList.splice(toIndex, 0, updatedDeal);
      set({ columns: { ...columns, [fromStageId]: sourceList } });
    } else {
      destList.splice(toIndex, 0, updatedDeal);
      set({
        columns: {
          ...columns,
          [fromStageId]: sourceList,
          [toStageId]: destList,
        },
      });
    }

    // ── API sync ───────────────────────────────────────────────────────────────
    try {
      await dealsApi.moveStage(dealId, {
        new_stage_id: toStageId,
        pipeline_id: pipelineId,
        performed_by_id: performedById,
      });
    } catch (err) {
      // Rollback to snapshot before optimistic update
      set({ columns, error: (err as Error).message });
    }
  },
}));
