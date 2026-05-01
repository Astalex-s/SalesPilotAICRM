import { Alert, Box, Skeleton, Typography } from '@mui/material';
import { DragDropContext, type DropResult } from 'react-beautiful-dnd';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/useAuthStore';
import { useKanbanStore } from '../../store/useKanbanStore';
import KanbanColumn from './KanbanColumn';

interface KanbanBoardProps {
  pipelineId: string;
}

/* ── Skeleton for loading state ── */
function BoardSkeleton() {
  return (
    <Box sx={{ display: 'flex', gap: 2.5, overflowX: 'auto', pb: 2, alignItems: 'flex-start' }}>
      {Array.from({ length: 4 }).map((_, i) => (
        <Box key={i} sx={{ minWidth: 272, flexShrink: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5, px: 0.5 }}>
            <Skeleton variant="text" width={100} height={22} />
            <Skeleton variant="rounded" width={32} height={20} sx={{ borderRadius: '20px' }} />
          </Box>
          <Box sx={{ borderRadius: '12px', bgcolor: '#F0F5FF', p: 1.25, minHeight: 200 }}>
            {Array.from({ length: 3 - i % 2 }).map((_, j) => (
              <Skeleton
                key={j}
                variant="rounded"
                height={96}
                sx={{ mb: 1.5, borderRadius: '12px' }}
              />
            ))}
          </Box>
        </Box>
      ))}
    </Box>
  );
}

/* ── Totals bar ── */
function TotalsBar({ pipeline, columns }: { pipeline: NonNullable<ReturnType<typeof useKanbanStore.getState>['pipeline']>; columns: ReturnType<typeof useKanbanStore.getState>['columns'] }) {
  const { t } = useTranslation();

  const totalValue = Object.values(columns)
    .flat()
    .filter((d) => d.status === 'open')
    .reduce((sum, d) => sum + Number(d.value_amount), 0);

  const totalDeals = Object.values(columns).flat().length;

  function fmt(n: number) {
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
    return `$${n}`;
  }

  return (
    <Box
      sx={{
        mt: 2.5,
        p: '14px 20px',
        background: '#FFFFFF',
        border: '1px solid #E2EAF4',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(13,33,68,0.06)',
        display: 'flex',
        alignItems: 'center',
        gap: 3,
      }}
    >
      <Box>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8' }}>
          {t('pipeline.totalValue')}
        </Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 20, fontWeight: 700, color: '#0D2144' }}>
          {fmt(totalValue)}
        </Typography>
      </Box>

      <Box sx={{ width: '1px', height: 36, bgcolor: '#E2EAF4' }} />

      <Box>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8' }}>
          {t('pipeline.totalDeals')}
        </Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 20, fontWeight: 700, color: '#0D2144' }}>
          {totalDeals}
        </Typography>
      </Box>

      <Box sx={{ flex: 1 }} />

      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
        {pipeline.name}
      </Typography>
    </Box>
  );
}

/* ── Main board ── */
export default function KanbanBoard({ pipelineId }: KanbanBoardProps) {
  const { pipeline, columns, loading, error, moveDeal } = useKanbanStore();
  const userId = useAuthStore((s) => s.user?.id ?? '');

  const onDragEnd = (result: DropResult) => {
    const { draggableId, source, destination } = result;
    if (!destination) return;
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) return;

    moveDeal({
      dealId: draggableId,
      fromStageId: source.droppableId,
      toStageId: destination.droppableId,
      toIndex: destination.index,
      pipelineId,
      performedById: userId,
    });
  };

  if (loading) return <BoardSkeleton />;

  if (error) {
    return (
      <Alert severity="error" sx={{ borderRadius: '12px' }}>
        {error}
      </Alert>
    );
  }

  if (!pipeline) return null;

  return (
    <Box>
      <DragDropContext onDragEnd={onDragEnd}>
        <Box
          sx={{
            display: 'flex',
            gap: 2.5,
            overflowX: 'auto',
            pb: 2,
            alignItems: 'flex-start',
          }}
        >
          {pipeline.stages.map((stage) => (
            <KanbanColumn
              key={stage.id}
              stage={stage}
              deals={columns[stage.id] ?? []}
            />
          ))}
        </Box>
      </DragDropContext>

      <TotalsBar pipeline={pipeline} columns={columns} />
    </Box>
  );
}
