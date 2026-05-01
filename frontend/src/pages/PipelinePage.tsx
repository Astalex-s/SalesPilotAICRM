import { Alert, Box, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import AddDealDialog from '../components/deals/AddDealDialog';
import KanbanBoard from '../components/kanban/KanbanBoard';
import PipelineManagerDialog from '../components/pipeline/PipelineManagerDialog';
import { useKanbanStore } from '../store/useKanbanStore';
import type { Pipeline } from '../types/pipeline';

export default function PipelinePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { pipelineId } = useParams<{ pipelineId: string }>();
  const { pipeline, allPipelines, loadBoard, loadPipelines, reloadBoard } = useKanbanStore();
  const [managerOpen, setManagerOpen] = useState(false);
  const [addDealStageId, setAddDealStageId] = useState<string | null>(null);

  useEffect(() => {
    loadPipelines();
  }, [loadPipelines]);

  useEffect(() => {
    if (pipelineId) loadBoard(pipelineId);
  }, [pipelineId, loadBoard]);

  const handlePipelineChange = (id: string) => {
    navigate(`/pipeline/${id}`);
  };

  const handlePipelinesChanged = (pipelines: Pipeline[]) => {
    // If current pipeline was deleted, navigate to first available
    if (pipelineId && !pipelines.find((p) => p.id === pipelineId)) {
      const first = pipelines[0];
      if (first) navigate(`/pipeline/${first.id}`);
    } else {
      // Reload board to reflect stage changes
      reloadBoard();
    }
  };

  if (!pipelineId) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144', mb: 2 }}>
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
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        mb: 3, gap: 2, flexWrap: 'wrap',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography sx={{
            fontFamily: 'Inter, sans-serif', fontSize: 22, fontWeight: 700,
            color: '#0D2144', letterSpacing: '-0.02em', whiteSpace: 'nowrap',
          }}>
            {t('pipeline.title')}
          </Typography>

          {/* Pipeline switcher */}
          {allPipelines.length > 1 && (
            <Box
              component="select"
              value={pipelineId}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handlePipelineChange(e.target.value)}
              sx={{
                px: '12px', py: '6px',
                border: '1px solid #E8EFF7', borderRadius: '8px',
                fontSize: 13, fontFamily: 'Inter, sans-serif', color: '#191C1E',
                background: '#fff', cursor: 'pointer', outline: 'none',
                '&:focus': { borderColor: '#00A8E8' },
              }}
            >
              {allPipelines.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </Box>
          )}

          {pipeline && allPipelines.length <= 1 && (
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#4B6080' }}>
              {pipeline.name}
            </Typography>
          )}
        </Box>

        {/* Manage button */}
        <Box
          component="button"
          onClick={() => setManagerOpen(true)}
          sx={{
            display: 'flex', alignItems: 'center', gap: 0.75,
            px: '14px', py: '8px',
            border: '1px solid #E8EFF7', borderRadius: '8px',
            bgcolor: '#fff', color: '#3E4850',
            fontSize: 13, fontWeight: 600, fontFamily: 'Inter, sans-serif',
            cursor: 'pointer',
            '&:hover': { borderColor: '#00A8E8', color: '#00A8E8', bgcolor: 'rgba(0,168,232,0.04)' },
            transition: 'all 0.15s',
          }}
        >
          <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
          </svg>
          {t('pipeline.manage')}
        </Box>
      </Box>

      <KanbanBoard
        pipelineId={pipelineId}
        onAddDeal={(stageId) => setAddDealStageId(stageId)}
      />

      <PipelineManagerDialog
        open={managerOpen}
        onClose={() => { setManagerOpen(false); reloadBoard(); }}
        onPipelinesChanged={handlePipelinesChanged}
      />

      <AddDealDialog
        open={addDealStageId !== null}
        onClose={() => setAddDealStageId(null)}
        pipeline={pipeline ?? null}
        defaultStageId={addDealStageId ?? undefined}
        onDealCreated={() => { setAddDealStageId(null); reloadBoard(); }}
      />
    </Box>
  );
}
