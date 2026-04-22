import { create } from 'zustand';
import { dealsApi } from '../api/deals';
import { pipelinesApi } from '../api/pipelines';
import { type Deal } from '../types/deal';
import { type Pipeline } from '../types/pipeline';

/** Columns indexed by stage_id → ordered list of deals. */
export type KanbanColumns = Record<string, Deal[]>;

interface KanbanState {
  pipeline: Pipeline | null;
  columns: KanbanColumns;
  loading: boolean;
  error: string | null;

  /** Load pipeline metadata + all its deals, build columns. */
  loadBoard: (pipelineId: string) => Promise<void>;

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
  columns: {},
  loading: false,
  error: null,

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
