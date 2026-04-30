import { Alert, Box, Typography } from '@mui/material';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import KanbanBoard from '../components/kanban/KanbanBoard';
import { useKanbanStore } from '../store/useKanbanStore';

export default function PipelinePage() {
  const { t } = useTranslation();
  const { pipelineId } = useParams<{ pipelineId: string }>();
  const { pipeline, loadBoard } = useKanbanStore();

  useEffect(() => {
    if (pipelineId) loadBoard(pipelineId);
  }, [pipelineId, loadBoard]);

  if (!pipelineId) {
    return (
      <Box>
        <Typography
          sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144', mb: 2 }}
        >
          {t('pipeline.title')}
        </Typography>
        <Alert severity="info" sx={{ borderRadius: '12px' }}>
          {t('pipeline.noPipeline')}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144', lineHeight: 1.2 }}
        >
          {t('pipeline.title')}
        </Typography>
        {pipeline && (
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#4B6080', mt: 0.5 }}>
            {pipeline.name}
          </Typography>
        )}
      </Box>

      <KanbanBoard pipelineId={pipelineId} />
    </Box>
  );
}
