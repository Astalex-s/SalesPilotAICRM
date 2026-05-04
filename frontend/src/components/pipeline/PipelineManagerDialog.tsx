import { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Dialog, DialogContent, Typography, useTheme } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { pipelinesApi } from '../../api/pipelines';
import { type Pipeline, type Stage } from '../../types/pipeline';

/* ── Design tokens ───────────────────────────────────────────────────────────── */
function useColors() {
  const theme = useTheme();
  const dark = theme.palette.mode === 'dark';
  return {
    cyan:   '#00A8E8',
    bg:     theme.palette.background.default,
    card:   theme.palette.background.paper,
    border: theme.palette.divider,
    text:   theme.palette.text.primary,
    sub:    theme.palette.text.secondary,
    muted:  dark ? '#7F93AC' : '#8FA3B8',
    hover:  dark ? 'rgba(255,255,255,0.05)' : '#F5F8FC',
    red:    '#EF4444',
  };
}

function makeInputSx(C: ReturnType<typeof useColors>) {
  return {
    width: '100%', px: '10px', py: '7px',
    border: `1px solid ${C.border}`, borderRadius: '8px',
    fontSize: 13, fontFamily: 'Inter, sans-serif', color: C.text, background: 'transparent',
    outline: 'none', transition: 'border-color 0.15s',
    '&:focus': { borderColor: C.cyan },
  };
}

/* ── Stage color presets ─────────────────────────────────────────────────────── */
const STAGE_COLORS = [
  '#00A8E8', '#10B981', '#F59E0B', '#EF4444',
  '#8B5CF6', '#EC4899', '#0D2144', '#64748B',
];

/* ── Icon button ─────────────────────────────────────────────────────────────── */
function IconBtn({
  title, onClick, danger, disabled, children,
}: {
  title?: string; onClick: (e: React.MouseEvent) => void; danger?: boolean; disabled?: boolean; children: React.ReactNode;
}) {
  const C = useColors();
  return (
    <Box
      component="button"
      title={title}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        width: 28, height: 28, border: 'none', borderRadius: '6px',
        bgcolor: 'transparent', cursor: disabled ? 'default' : 'pointer',
        color: disabled ? '#CBD5E0' : danger ? C.red : C.muted,
        opacity: disabled ? 0.4 : 1,
        '&:hover': disabled ? {} : { bgcolor: danger ? '#FFF5F5' : C.hover, color: danger ? C.red : C.text },
        transition: 'all 0.15s',
        flexShrink: 0,
      }}
    >
      {children}
    </Box>
  );
}

/* ── SVG icons ───────────────────────────────────────────────────────────────── */
const PenIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
);
const TrashIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14H6L5 6" />
    <path d="M10 11v6M14 11v6M9 6V4h6v2" />
  </svg>
);
const UpIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polyline points="18 15 12 9 6 15" />
  </svg>
);
const DownIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
);
const PlusIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);
const CheckIcon = () => (
  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

/* ── Color picker row ────────────────────────────────────────────────────────── */
function ColorPicker({
  value, onChange,
}: {
  value: string | null; onChange: (c: string | null) => void;
}) {
  const C = useColors();
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexWrap: 'wrap' }}>
      {/* "No color" swatch */}
      <Box
        onClick={() => onChange(null)}
        title="No color"
        sx={{
          width: 22, height: 22, borderRadius: '50%',
          border: `2px solid ${value === null ? C.cyan : C.border}`,
          bgcolor: C.card, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          '&:hover': { borderColor: C.cyan },
          transition: 'border-color 0.15s',
        }}
      >
        <svg width={10} height={10} viewBox="0 0 24 24" stroke="#CBD5E0" strokeWidth="2">
          <line x1="4" y1="4" x2="20" y2="20" /><line x1="20" y1="4" x2="4" y2="20" />
        </svg>
      </Box>
      {STAGE_COLORS.map((c) => (
        <Box
          key={c}
          onClick={() => onChange(c)}
          title={c}
          sx={{
            width: 22, height: 22, borderRadius: '50%', bgcolor: c,
            border: `2px solid ${value === c ? C.cyan : 'transparent'}`,
            cursor: 'pointer', transition: 'transform 0.12s, border 0.12s',
            '&:hover': { transform: 'scale(1.2)' },
          }}
        />
      ))}
    </Box>
  );
}

/* ── Stage row (view mode) ───────────────────────────────────────────────────── */
function StageRow({
  stage, isFirst, isLast, pipelineId, onUpdated,
}: {
  stage: Stage; isFirst: boolean; isLast: boolean;
  pipelineId: string; onUpdated: (p: Pipeline) => void;
}) {
  const { t } = useTranslation();
  const C = useColors();
  const inputSx = makeInputSx(C);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(stage.name);
  const [prob, setProb] = useState(String(Math.round(stage.probability * 100)));
  const [color, setColor] = useState<string | null>(stage.color ?? null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { if (editing) inputRef.current?.focus(); }, [editing]);

  const handleSave = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      const probVal = Math.min(1, Math.max(0, (Number(prob) || 50) / 100));
      const updated = await pipelinesApi.updateStage(pipelineId, stage.id, {
        name: name.trim(),
        probability: probVal,
        color: color ?? undefined,
        clear_color: color === null,
      });
      onUpdated(updated);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      const updated = await pipelinesApi.deleteStage(pipelineId, stage.id);
      onUpdated(updated);
    } finally {
      setDeleting(false);
    }
  };

  const handleMoveOrder = async (direction: 'up' | 'down') => {
    onUpdated({ id: pipelineId, name: '', owner_id: '', stages: [], is_active: true, created_at: '', _reorderStage: { stageId: stage.id, direction } } as any);
  };

  if (editing) {
    return (
      <Box sx={{
        p: 1.5, borderRadius: '10px', border: `1px solid ${C.cyan}`,
        bgcolor: 'rgba(0,168,232,0.04)', mb: 1,
      }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 1, mb: 1 }}>
          <Box
            component="input"
            ref={inputRef}
            value={name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
            onKeyDown={(e: React.KeyboardEvent) => { if (e.key === 'Enter') handleSave(); if (e.key === 'Escape') setEditing(false); }}
            sx={inputSx}
          />
          <Box
            component="input"
            type="number"
            min={0} max={100}
            value={prob}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setProb(e.target.value)}
            title={t('pipelineManager.probability')}
            sx={{ ...inputSx, width: 64, textAlign: 'center' }}
          />
        </Box>
        <Box sx={{ mb: 1.5 }}>
          <Typography sx={{ fontSize: 11, fontWeight: 600, color: C.muted, fontFamily: 'Inter, sans-serif', mb: 0.5, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {t('pipelineManager.stageColor')}
          </Typography>
          <ColorPicker value={color} onChange={setColor} />
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Box
            component="button"
            onClick={handleSave}
            disabled={saving}
            sx={{
              px: 2, py: '6px', border: 'none', borderRadius: '7px',
              bgcolor: C.cyan, color: '#fff',
              fontSize: 12, fontWeight: 600, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5,
              '&:hover': { bgcolor: '#0096D1' }, '&:disabled': { opacity: 0.6 },
            }}
          >
            {saving ? <CircularProgress size={12} sx={{ color: '#fff' }} /> : <CheckIcon />}
            {t('pipelineManager.save')}
          </Box>
          <Box
            component="button"
            onClick={() => { setEditing(false); setName(stage.name); setProb(String(Math.round(stage.probability * 100))); setColor(stage.color ?? null); }}
            sx={{
              px: 2, py: '6px', border: `1px solid ${C.border}`, borderRadius: '7px',
              bgcolor: 'transparent', color: C.sub, fontSize: 12, fontWeight: 600,
              fontFamily: 'Inter, sans-serif', cursor: 'pointer',
              '&:hover': { bgcolor: C.hover },
            }}
          >
            {t('pipelineManager.cancel')}
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{
      display: 'flex', alignItems: 'center', gap: 1,
      px: 1.5, py: 1, borderRadius: '8px',
      border: `1px solid ${C.border}`, bgcolor: C.card, mb: 0.75,
      '&:hover': { bgcolor: C.hover },
      transition: 'background 0.12s',
    }}>
      {/* Color dot */}
      <Box sx={{
        width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
        bgcolor: stage.color ?? C.border,
        border: stage.color ? 'none' : `1px dashed ${C.border}`,
      }} />

      {/* Name */}
      <Typography sx={{ flex: 1, fontSize: 13, fontWeight: 500, color: C.text, fontFamily: 'Inter, sans-serif', minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {stage.name}
      </Typography>

      {/* Probability badge */}
      <Box sx={{
        px: '6px', py: '2px', borderRadius: '999px',
        bgcolor: 'rgba(0,168,232,0.08)',
        fontSize: 11, fontWeight: 600, color: C.cyan,
        fontFamily: 'Inter, sans-serif', flexShrink: 0,
      }}>
        {Math.round(stage.probability * 100)}%
      </Box>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 0.25 }}>
        <IconBtn title="Move up" onClick={() => handleMoveOrder('up')} disabled={isFirst}>
          <UpIcon />
        </IconBtn>
        <IconBtn title="Move down" onClick={() => handleMoveOrder('down')} disabled={isLast}>
          <DownIcon />
        </IconBtn>
        <IconBtn title={t('pipelineManager.editStage')} onClick={() => setEditing(true)}>
          <PenIcon />
        </IconBtn>
        <IconBtn title={t('pipelineManager.deleteStage')} onClick={handleDelete} danger>
          {deleting ? <CircularProgress size={12} sx={{ color: C.red }} /> : <TrashIcon />}
        </IconBtn>
      </Box>
    </Box>
  );
}

/* ── Add stage form ──────────────────────────────────────────────────────────── */
function AddStageForm({
  pipelineId, onAdded,
}: { pipelineId: string; onAdded: (p: Pipeline) => void }) {
  const { t } = useTranslation();
  const C = useColors();
  const inputSx = makeInputSx(C);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [prob, setProb] = useState('50');
  const [color, setColor] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleAdd = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      const probVal = Math.min(1, Math.max(0, (Number(prob) || 50) / 100));
      const updated = await pipelinesApi.addStage(pipelineId, {
        name: name.trim(),
        probability: probVal,
        color: color ?? undefined,
      });
      onAdded(updated);
      setName(''); setProb('50'); setColor(null); setOpen(false);
    } finally {
      setSaving(false);
    }
  };

  if (!open) {
    return (
      <Box
        component="button"
        onClick={() => setOpen(true)}
        sx={{
          display: 'flex', alignItems: 'center', gap: 0.75,
          width: '100%', px: 1.5, py: 1,
          border: `1px dashed ${C.border}`, borderRadius: '8px',
          bgcolor: 'transparent', cursor: 'pointer', color: C.muted,
          fontSize: 13, fontFamily: 'Inter, sans-serif',
          '&:hover': { borderColor: C.cyan, color: C.cyan, bgcolor: 'rgba(0,168,232,0.04)' },
          transition: 'all 0.15s',
        }}
      >
        <PlusIcon />
        {t('pipelineManager.addStage')}
      </Box>
    );
  }

  return (
    <Box sx={{
      p: 1.5, borderRadius: '10px',
      border: `1px solid ${C.cyan}`, bgcolor: 'rgba(0,168,232,0.04)',
    }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 1, mb: 1 }}>
        <Box
          component="input"
          autoFocus
          placeholder={t('pipelineManager.stageNamePlaceholder')}
          value={name}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent) => { if (e.key === 'Enter') handleAdd(); if (e.key === 'Escape') setOpen(false); }}
          sx={inputSx}
        />
        <Box
          component="input"
          type="number" min={0} max={100}
          value={prob}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setProb(e.target.value)}
          title={t('pipelineManager.probability')}
          sx={{ ...inputSx, width: 64, textAlign: 'center' }}
        />
      </Box>
      <Box sx={{ mb: 1.5 }}>
        <Typography sx={{ fontSize: 11, fontWeight: 600, color: C.muted, fontFamily: 'Inter, sans-serif', mb: 0.5, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {t('pipelineManager.stageColor')}
        </Typography>
        <ColorPicker value={color} onChange={setColor} />
      </Box>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Box
          component="button"
          onClick={handleAdd}
          disabled={saving || !name.trim()}
          sx={{
            px: 2, py: '6px', border: 'none', borderRadius: '7px',
            bgcolor: C.cyan, color: '#fff',
            fontSize: 12, fontWeight: 600, fontFamily: 'Inter, sans-serif',
            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5,
            '&:hover': { bgcolor: '#0096D1' }, '&:disabled': { opacity: 0.6, cursor: 'not-allowed' },
          }}
        >
          {saving ? <CircularProgress size={12} sx={{ color: '#fff' }} /> : <PlusIcon />}
          {t('pipelineManager.addStage')}
        </Box>
        <Box
          component="button"
          onClick={() => { setOpen(false); setName(''); }}
          sx={{
            px: 2, py: '6px', border: `1px solid ${C.border}`, borderRadius: '7px',
            bgcolor: 'transparent', color: C.sub,
            fontSize: 12, fontWeight: 600, fontFamily: 'Inter, sans-serif', cursor: 'pointer',
            '&:hover': { bgcolor: C.hover },
          }}
        >
          {t('pipelineManager.cancel')}
        </Box>
      </Box>
    </Box>
  );
}

/* ── Main dialog ─────────────────────────────────────────────────────────────── */
interface PipelineManagerDialogProps {
  open: boolean;
  onClose: () => void;
  onPipelinesChanged: (pipelines: Pipeline[]) => void;
}

export default function PipelineManagerDialog({
  open, onClose, onPipelinesChanged,
}: PipelineManagerDialogProps) {
  const { t } = useTranslation();
  const C = useColors();
  const inputSx = makeInputSx(C);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [newPipelineName, setNewPipelineName] = useState('');
  const [creatingPipeline, setCreatingPipeline] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const selectedPipeline = pipelines.find((p) => p.id === selectedId) ?? null;

  useEffect(() => {
    if (open) loadPipelines();
  }, [open]);

  const loadPipelines = async () => {
    setLoading(true);
    try {
      const list = await pipelinesApi.list();
      setPipelines(list);
      if (list.length && !selectedId) setSelectedId(list[0].id);
    } finally {
      setLoading(false);
    }
  };

  const syncPipeline = (updated: Pipeline) => {
    if ((updated as any)._reorderStage) {
      const { stageId, direction } = (updated as any)._reorderStage;
      const pipeline = pipelines.find((p) => p.id === updated.id);
      if (!pipeline) return;
      reorderStage(pipeline, stageId, direction);
      return;
    }
    setPipelines((prev) => prev.map((p) => p.id === updated.id ? updated : p));
    onPipelinesChanged(pipelines.map((p) => p.id === updated.id ? updated : p));
  };

  const reorderStage = async (pipeline: Pipeline, stageId: string, direction: 'up' | 'down') => {
    const stages = [...pipeline.stages].sort((a, b) => a.order - b.order);
    const idx = stages.findIndex((s) => s.id === stageId);
    if (idx === -1) return;
    const swapIdx = direction === 'up' ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= stages.length) return;

    const stageA = stages[idx];
    try {
      await pipelinesApi.updateStage(pipeline.id, stageA.id, { probability: stageA.probability, name: stageA.name, color: stageA.color, clear_color: stageA.color === null });
      await pipelinesApi.updateStage(pipeline.id, stageA.id, { name: stageA.name, probability: stageA.probability });
      const refreshed = await pipelinesApi.get(pipeline.id);
      syncPipeline(refreshed);
    } catch (_) {
      const refreshed = await pipelinesApi.get(pipeline.id);
      syncPipeline(refreshed);
    }
  };

  const handleCreatePipeline = async () => {
    if (!newPipelineName.trim()) return;
    setCreatingPipeline(true);
    try {
      const created = await pipelinesApi.create(newPipelineName.trim());
      const updated = [...pipelines, created];
      setPipelines(updated);
      onPipelinesChanged(updated);
      setSelectedId(created.id);
      setNewPipelineName('');
      setShowCreateForm(false);
    } finally {
      setCreatingPipeline(false);
    }
  };

  const handleRenamePipeline = async (id: string) => {
    if (!renameValue.trim()) return;
    try {
      const updated = await pipelinesApi.update(id, renameValue.trim());
      const newList = pipelines.map((p) => p.id === id ? updated : p);
      setPipelines(newList);
      onPipelinesChanged(newList);
      setRenamingId(null);
    } catch (_) {}
  };

  const handleDeletePipeline = async (id: string) => {
    setDeletingId(id);
    try {
      await pipelinesApi.delete(id);
      const newList = pipelines.filter((p) => p.id !== id);
      setPipelines(newList);
      onPipelinesChanged(newList);
      if (selectedId === id) setSelectedId(newList[0]?.id ?? null);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        elevation: 0,
        sx: {
          borderRadius: '16px', border: '1px solid', borderColor: 'divider',
          boxShadow: '0 16px 48px rgba(13,33,68,0.14)',
          height: '80vh', display: 'flex', flexDirection: 'column',
        },
      }}
    >
      {/* Header */}
      <Box sx={{
        px: 3, py: 2.5, borderBottom: `1px solid ${C.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <Typography sx={{ fontSize: 18, fontWeight: 700, color: C.text, fontFamily: 'Inter, sans-serif' }}>
          {t('pipelineManager.title')}
        </Typography>
        <Box
          onClick={onClose}
          sx={{ color: C.muted, cursor: 'pointer', display: 'flex', p: '6px', borderRadius: '8px', '&:hover': { color: C.text, bgcolor: C.hover } }}
        >
          <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </Box>
      </Box>

      <DialogContent sx={{ p: 0, display: 'flex', flex: 1, overflow: 'hidden' }}>
        {loading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
            <CircularProgress sx={{ color: C.cyan }} />
          </Box>
        ) : (
          <>
            {/* ── Left panel: pipeline list ── */}
            <Box sx={{
              width: 220, flexShrink: 0,
              borderRight: `1px solid ${C.border}`,
              display: 'flex', flexDirection: 'column',
              bgcolor: C.bg,
            }}>
              <Box sx={{ p: 1.5, flex: 1, overflowY: 'auto' }}>
                {pipelines.map((p) => (
                  <Box key={p.id}>
                    {renamingId === p.id ? (
                      <Box sx={{ display: 'flex', gap: 0.5, mb: 0.5 }}>
                        <Box
                          component="input"
                          autoFocus
                          value={renameValue}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRenameValue(e.target.value)}
                          onKeyDown={(e: React.KeyboardEvent) => {
                            if (e.key === 'Enter') handleRenamePipeline(p.id);
                            if (e.key === 'Escape') setRenamingId(null);
                          }}
                          sx={{ ...inputSx, py: '5px', flex: 1 }}
                        />
                        <IconBtn onClick={() => handleRenamePipeline(p.id)}>
                          <CheckIcon />
                        </IconBtn>
                      </Box>
                    ) : (
                      <Box
                        onClick={() => setSelectedId(p.id)}
                        sx={{
                          display: 'flex', alignItems: 'center',
                          px: 1.5, py: 0.875, borderRadius: '8px', mb: 0.25,
                          bgcolor: selectedId === p.id ? 'rgba(0,168,232,0.1)' : 'transparent',
                          cursor: 'pointer',
                          '&:hover': {
                            bgcolor: selectedId === p.id ? 'rgba(0,168,232,0.1)' : C.hover,
                            '& .pipeline-item-actions': { opacity: 1 },
                          },
                          transition: 'background 0.12s',
                          border: selectedId === p.id ? `1px solid rgba(0,168,232,0.25)` : '1px solid transparent',
                          gap: 0.75,
                        }}
                      >
                        {selectedId === p.id && (
                          <Box sx={{ width: 3, height: 16, borderRadius: '2px', bgcolor: C.cyan, flexShrink: 0 }} />
                        )}
                        <Typography sx={{
                          flex: 1, fontSize: 13, fontWeight: selectedId === p.id ? 600 : 400,
                          color: selectedId === p.id ? C.cyan : C.text,
                          fontFamily: 'Inter, sans-serif', minWidth: 0,
                          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                        }}>
                          {p.name}
                        </Typography>
                        <Box className="pipeline-item-actions" sx={{ display: 'flex', gap: 0.25, opacity: 0, transition: 'opacity 0.15s' }}>
                          <IconBtn title={t('pipelineManager.renamePipeline')} onClick={(e) => { e.stopPropagation(); setRenamingId(p.id); setRenameValue(p.name); }}>
                            <PenIcon />
                          </IconBtn>
                          <IconBtn title={t('pipelineManager.deletePipeline')} onClick={(e) => { e.stopPropagation(); handleDeletePipeline(p.id); }} danger>
                            {deletingId === p.id ? <CircularProgress size={10} sx={{ color: C.red }} /> : <TrashIcon />}
                          </IconBtn>
                        </Box>
                      </Box>
                    )}
                  </Box>
                ))}
              </Box>

              {/* Create pipeline */}
              <Box sx={{ p: 1.5, borderTop: `1px solid ${C.border}` }}>
                {showCreateForm ? (
                  <Box>
                    <Box
                      component="input"
                      autoFocus
                      placeholder={t('pipelineManager.pipelineNamePlaceholder')}
                      value={newPipelineName}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPipelineName(e.target.value)}
                      onKeyDown={(e: React.KeyboardEvent) => {
                        if (e.key === 'Enter') handleCreatePipeline();
                        if (e.key === 'Escape') setShowCreateForm(false);
                      }}
                      sx={{ ...inputSx, mb: 0.75 }}
                    />
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Box
                        component="button"
                        onClick={handleCreatePipeline}
                        disabled={creatingPipeline || !newPipelineName.trim()}
                        sx={{
                          flex: 1, py: '6px', border: 'none', borderRadius: '7px',
                          bgcolor: C.cyan, color: '#fff',
                          fontSize: 12, fontWeight: 600, fontFamily: 'Inter, sans-serif',
                          cursor: 'pointer', '&:disabled': { opacity: 0.6, cursor: 'not-allowed' },
                        }}
                      >
                        {creatingPipeline ? '...' : t('pipelineManager.create')}
                      </Box>
                      <Box
                        component="button"
                        onClick={() => { setShowCreateForm(false); setNewPipelineName(''); }}
                        sx={{
                          px: 1.5, py: '6px', border: `1px solid ${C.border}`, borderRadius: '7px',
                          bgcolor: 'transparent', color: C.sub, fontSize: 12, fontFamily: 'Inter, sans-serif', cursor: 'pointer',
                        }}
                      >
                        ✕
                      </Box>
                    </Box>
                  </Box>
                ) : (
                  <Box
                    component="button"
                    onClick={() => setShowCreateForm(true)}
                    sx={{
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5,
                      width: '100%', py: '7px', border: `1px dashed ${C.border}`, borderRadius: '8px',
                      bgcolor: 'transparent', cursor: 'pointer', color: C.muted,
                      fontSize: 12, fontFamily: 'Inter, sans-serif',
                      '&:hover': { borderColor: C.cyan, color: C.cyan },
                      transition: 'all 0.15s',
                    }}
                  >
                    <PlusIcon />
                    {t('pipelineManager.newPipeline')}
                  </Box>
                )}
              </Box>
            </Box>

            {/* ── Right panel: stages ── */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              {selectedPipeline ? (
                <>
                  <Box sx={{ px: 3, py: 2, borderBottom: `1px solid ${C.border}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography sx={{ fontSize: 15, fontWeight: 700, color: C.text, fontFamily: 'Inter, sans-serif' }}>
                        {selectedPipeline.name}
                      </Typography>
                      <Typography sx={{ fontSize: 12, color: C.muted, fontFamily: 'Inter, sans-serif', mt: '2px' }}>
                        {t('pipelineManager.stagesCount', { count: selectedPipeline.stages.length })}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography sx={{ fontSize: 11, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                        {t('pipelineManager.probabilityHint')}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ flex: 1, overflowY: 'auto', p: 2.5 }}>
                    {/* Column headers */}
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 1, px: 1.5, mb: 0.75 }}>
                      <Typography sx={{ fontSize: 11, fontWeight: 600, color: C.muted, fontFamily: 'Inter, sans-serif', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {t('pipelineManager.stageName')}
                      </Typography>
                      <Typography sx={{ fontSize: 11, fontWeight: 600, color: C.muted, fontFamily: 'Inter, sans-serif', textTransform: 'uppercase', letterSpacing: '0.05em', width: 64, textAlign: 'center' }}>
                        {t('pipelineManager.probability')}
                      </Typography>
                    </Box>

                    {selectedPipeline.stages.length === 0 ? (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography sx={{ fontSize: 14, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                          {t('pipelineManager.noStages')}
                        </Typography>
                      </Box>
                    ) : (
                      [...selectedPipeline.stages]
                        .sort((a, b) => a.order - b.order)
                        .map((stage, idx, arr) => (
                          <StageRow
                            key={stage.id}
                            stage={stage}
                            isFirst={idx === 0}
                            isLast={idx === arr.length - 1}
                            pipelineId={selectedPipeline.id}
                            onUpdated={syncPipeline}
                          />
                        ))
                    )}

                    <Box sx={{ mt: 1 }}>
                      <AddStageForm pipelineId={selectedPipeline.id} onAdded={syncPipeline} />
                    </Box>
                  </Box>
                </>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
                  <Typography sx={{ fontSize: 14, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                    {t('pipelineManager.selectPipeline')}
                  </Typography>
                </Box>
              )}
            </Box>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
