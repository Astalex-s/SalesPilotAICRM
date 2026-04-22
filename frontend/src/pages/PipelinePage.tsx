import { Alert, Box, Typography } from '@mui/material';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import KanbanBoard from '../components/kanban/KanbanBoard';
import { useKanbanStore } from '../store/useKanbanStore';

export default function PipelinePage() {
  const { pipelineId } = useParams<{ pipelineId: string }>();
  const loadBoard = useKanbanStore((s) => s.loadBoard);

  useEffect(() => {
    if (pipelineId) {
      loadBoard(pipelineId);
    }
  }, [pipelineId, loadBoard]);

  if (!pipelineId) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Pipeline
        </Typography>
        <Alert severity="info">No pipeline selected.</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Pipeline
      </Typography>
      <KanbanBoard pipelineId={pipelineId} />
    </Box>
  );
}
