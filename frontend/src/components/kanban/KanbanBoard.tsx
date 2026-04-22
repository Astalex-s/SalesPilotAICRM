import { Alert, Box, CircularProgress, Typography } from '@mui/material';
import { type DropResult, DragDropContext } from 'react-beautiful-dnd';
import { useKanbanStore } from '../../store/useKanbanStore';
import KanbanColumn from './KanbanColumn';

/** Placeholder owner ID — replace with auth context in a future step. */
const PLACEHOLDER_OWNER_ID = '00000000-0000-0000-0000-000000000001';

interface KanbanBoardProps {
  pipelineId: string;
}

export default function KanbanBoard({ pipelineId }: KanbanBoardProps) {
  const { pipeline, columns, loading, error, moveDeal } = useKanbanStore();

  const onDragEnd = (result: DropResult) => {
    const { draggableId, source, destination } = result;
    if (!destination) return;
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return;
    }

    moveDeal({
      dealId: draggableId,
      fromStageId: source.droppableId,
      toStageId: destination.droppableId,
      toIndex: destination.index,
      pipelineId,
      performedById: PLACEHOLDER_OWNER_ID,
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!pipeline) return null;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} mb={2}>
        {pipeline.name}
      </Typography>

      <DragDropContext onDragEnd={onDragEnd}>
        <Box
          sx={{
            display: 'flex',
            gap: 2,
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
    </Box>
  );
}
