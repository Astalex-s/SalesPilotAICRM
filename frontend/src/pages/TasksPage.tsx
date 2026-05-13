import AddIcon from '@mui/icons-material/Add';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import EmptyState from '../components/common/EmptyState';
import AddTaskDialog from '../components/tasks/AddTaskDialog';
import { useTaskStore } from '../store/useTaskStore';
import { type CrmTask, type TaskStatus } from '../types/task';

const STATUS_STYLE: Record<TaskStatus, { bg: string; color: string }> = {
  pending:     { bg: 'rgba(0,168,232,0.10)',   color: '#0090CC' },
  in_progress: { bg: 'rgba(245,158,11,0.10)',  color: '#D97706' },
  done:        { bg: 'rgba(16,185,129,0.10)',  color: '#059669' },
  cancelled:   { bg: 'rgba(148,163,184,0.10)', color: '#64748B' },
};

const FILTER_OPTIONS: Array<TaskStatus | 'all' | 'overdue'> = [
  'all', 'pending', 'in_progress', 'done', 'cancelled', 'overdue',
];

function TaskRow({ task, onDone, onDelete }: { task: CrmTask; onDone: (id: string) => void; onDelete: (id: string) => void }) {
  const { t } = useTranslation();
  const st = STATUS_STYLE[task.status];
  const [deleting, setDeleting] = useState(false);
  const [completing, setCompleting] = useState(false);

  const handleDone = async () => {
    setCompleting(true);
    try { await onDone(task.id); } finally { setCompleting(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try { await onDelete(task.id); } finally { setDeleting(false); }
  };

  return (
    <TableRow sx={{ height: 56, '& td': { border: 'none', borderTop: '1px solid #F0F5FF' }, '&:hover': { bgcolor: '#F0F5FF' } }}>
      {/* Title + description */}
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {task.is_overdue && (
            <Tooltip title={t('tasks.overdue')}>
              <WarningAmberIcon sx={{ fontSize: 15, color: '#F59E0B', flexShrink: 0 }} />
            </Tooltip>
          )}
          <Box>
            <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: '#0D2144', lineHeight: 1.2 }}>
              {task.title}
            </Typography>
            {task.description && (
              <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', lineHeight: 1.3 }}>
                {task.description.length > 60 ? task.description.slice(0, 60) + '…' : task.description}
              </Typography>
            )}
          </Box>
        </Box>
      </TableCell>

      {/* Status */}
      <TableCell>
        <Box sx={{ display: 'inline-flex', px: 1.25, py: 0.4, borderRadius: '20px', bgcolor: st.bg, color: st.color, fontFamily: 'Inter', fontSize: 12, fontWeight: 600 }}>
          {t(`tasks.status.${task.status}`)}
        </Box>
      </TableCell>

      {/* Due date */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: task.is_overdue ? '#EF4444' : '#94A3B8', fontWeight: task.is_overdue ? 600 : 400 }}>
          {task.due_date
            ? new Date(task.due_date).toLocaleString(undefined, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
            : '—'}
        </Typography>
      </TableCell>

      {/* Created */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
          {new Date(task.created_at).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })}
        </Typography>
      </TableCell>

      {/* Context */}
      <TableCell>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {task.lead_id && (
            <Chip label={t('tasks.linkedLead')} size="small" sx={{ fontSize: 10, height: 18, bgcolor: 'rgba(139,92,246,0.10)', color: '#7C3AED' }} />
          )}
          {task.deal_id && (
            <Chip label={t('tasks.linkedDeal')} size="small" sx={{ fontSize: 10, height: 18, bgcolor: 'rgba(16,185,129,0.10)', color: '#059669' }} />
          )}
        </Box>
      </TableCell>

      {/* Actions */}
      <TableCell>
        <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
          {task.status !== 'done' && task.status !== 'cancelled' && (
            <Tooltip title={t('tasks.markDone')}>
              <Box
                component="button"
                onClick={handleDone}
                disabled={completing}
                sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #D1FAE5', bgcolor: '#F0FDF4', color: '#10B981', cursor: 'pointer', '&:hover': { bgcolor: '#D1FAE5' }, '&:disabled': { opacity: 0.5, cursor: 'default' } }}
              >
                {completing ? <CircularProgress size={14} sx={{ color: '#10B981' }} /> : <CheckCircleOutlineIcon sx={{ fontSize: 15 }} />}
              </Box>
            </Tooltip>
          )}
          <Tooltip title={t('tasks.delete')}>
            <Box
              component="button"
              onClick={handleDelete}
              disabled={deleting}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #FEE2E2', bgcolor: '#FFF5F5', color: '#EF4444', cursor: 'pointer', '&:hover': { bgcolor: '#FEE2E2' }, '&:disabled': { opacity: 0.5, cursor: 'default' } }}
            >
              {deleting ? <CircularProgress size={14} sx={{ color: '#EF4444' }} /> : <DeleteOutlineIcon sx={{ fontSize: 15 }} />}
            </Box>
          </Tooltip>
        </Box>
      </TableCell>
    </TableRow>
  );
}

/* ── Mobile card for a single task ── */
function TaskMobileCard({ task, onDone, onDelete }: { task: CrmTask; onDone: (id: string) => void; onDelete: (id: string) => void }) {
  const { t } = useTranslation();
  const st = STATUS_STYLE[task.status];

  return (
    <Box sx={{ p: 2, background: '#FFFFFF', border: '1px solid #E2EAF4', borderRadius: '12px', boxShadow: '0 2px 8px rgba(13,33,68,0.06)' }}>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 1, mb: 0.75 }}>
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {task.is_overdue && <WarningAmberIcon sx={{ fontSize: 15, color: '#F59E0B', flexShrink: 0 }} />}
            <Typography noWrap sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: '#0D2144' }}>
              {task.title}
            </Typography>
          </Box>
          {task.description && (
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', mt: 0.25 }}>
              {task.description.length > 80 ? task.description.slice(0, 80) + '…' : task.description}
            </Typography>
          )}
        </Box>
        <Box sx={{ display: 'inline-flex', px: 1.25, py: 0.4, borderRadius: '20px', bgcolor: st.bg, color: st.color, fontFamily: 'Inter', fontSize: 12, fontWeight: 600, flexShrink: 0 }}>
          {t(`tasks.status.${task.status}`)}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: task.is_overdue ? '#EF4444' : '#94A3B8', fontWeight: task.is_overdue ? 600 : 400 }}>
            {task.due_date ? new Date(task.due_date).toLocaleDateString(undefined, { day: '2-digit', month: 'short' }) : '—'}
          </Typography>
          {task.lead_id && <Chip label={t('tasks.linkedLead')} size="small" sx={{ fontSize: 10, height: 18, bgcolor: 'rgba(139,92,246,0.10)', color: '#7C3AED' }} />}
          {task.deal_id && <Chip label={t('tasks.linkedDeal')} size="small" sx={{ fontSize: 10, height: 18, bgcolor: 'rgba(16,185,129,0.10)', color: '#059669' }} />}
        </Box>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {task.status !== 'done' && task.status !== 'cancelled' && (
            <Box component="button" onClick={() => onDone(task.id)} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #D1FAE5', bgcolor: '#F0FDF4', color: '#10B981', cursor: 'pointer' }}>
              <CheckCircleOutlineIcon sx={{ fontSize: 15 }} />
            </Box>
          )}
          <Box component="button" onClick={() => onDelete(task.id)} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #FEE2E2', bgcolor: '#FFF5F5', color: '#EF4444', cursor: 'pointer' }}>
            <DeleteOutlineIcon sx={{ fontSize: 15 }} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default function TasksPage() {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { tasks, loading, error, fetchTasks, updateTask, deleteTask } = useTaskStore();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [filter, setFilter] = useState<TaskStatus | 'all' | 'overdue'>('all');

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filtered = tasks.filter((task) => {
    if (filter === 'all') return true;
    if (filter === 'overdue') return task.is_overdue;
    return task.status === filter;
  });

  const handleDone = async (taskId: string) => {
    await updateTask(taskId, { status: 'done' });
  };

  const handleDelete = async (taskId: string) => {
    await deleteTask(taskId);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3, flexWrap: 'wrap', gap: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: { xs: 20, md: 24 }, fontWeight: 700, color: '#0D2144' }}>
            {t('tasks.title')}
          </Typography>
          {!loading && (
            <Box sx={{ px: 1.5, py: 0.25, borderRadius: '20px', bgcolor: '#E8F4FF', color: '#00A8E8', fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600 }}>
              {filtered.length}
            </Box>
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{ bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14, borderRadius: '10px', px: 2.5, textTransform: 'none', boxShadow: 'none', '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' } }}
        >
          {t('tasks.addTask')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

      {/* Filter pills */}
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2.5 }}>
        {FILTER_OPTIONS.map((opt) => {
          const active = filter === opt;
          return (
            <Box
              key={opt}
              onClick={() => setFilter(opt)}
              sx={{ px: 1.75, py: 0.6, borderRadius: '20px', fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: active ? 600 : 500, cursor: 'pointer', transition: 'all 0.15s', bgcolor: active ? '#00A8E8' : '#FFFFFF', color: active ? '#FFFFFF' : '#4B6080', border: `1px solid ${active ? '#00A8E8' : '#E2EAF4'}`, '&:hover': { bgcolor: active ? '#0090CC' : '#F0F5FF', borderColor: active ? '#0090CC' : '#CBD5E8' } }}
            >
              {opt === 'all' ? t('tasks.filterAll') : opt === 'overdue' ? t('tasks.filterOverdue') : t(`tasks.status.${opt}`)}
            </Box>
          );
        })}
      </Box>

      {/* Mobile card list */}
      {isMobile ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} variant="rounded" height={80} sx={{ borderRadius: '12px' }} />
            ))
          ) : filtered.length === 0 ? (
            <EmptyState icon="tasks" title={t('tasks.noTasks')} subtitle={t('tasks.noTasksSubtitle')} action={{ label: t('tasks.addTask'), onClick: () => setDialogOpen(true) }} />
          ) : (
            filtered.map((task) => (
              <TaskMobileCard key={task.id} task={task} onDone={handleDone} onDelete={handleDelete} />
            ))
          )}
        </Box>
      ) : (
      /* Desktop table */
      <Box sx={{ background: '#FFFFFF', border: '1px solid #E2EAF4', borderRadius: '16px', boxShadow: '0 4px 24px rgba(13,33,68,0.07)', overflowX: 'auto' }}>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {[
                [t('tasks.table.title'), undefined],
                [t('tasks.table.status'), '130px'],
                [t('tasks.table.dueDate'), '180px'],
                [t('tasks.table.created'), '140px'],
                [t('tasks.table.context'), '120px'],
                ['', '80px'],
              ].map(([label, width], i) => (
                <TableCell key={i} sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8', border: 'none', py: 1.5, width }}>
                  {label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i} sx={{ height: 56 }}>
                  {Array.from({ length: 6 }).map((__, j) => (
                    <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                      <Skeleton variant="text" width="80%" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ border: 'none' }}>
                  <EmptyState
                    icon="tasks"
                    title={t('tasks.noTasks')}
                    subtitle={t('tasks.noTasksSubtitle')}
                    action={{ label: t('tasks.addTask'), onClick: () => setDialogOpen(true) }}
                  />
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((task) => (
                <TaskRow key={task.id} task={task} onDone={handleDone} onDelete={handleDelete} />
              ))
            )}
          </TableBody>
        </Table>
      </Box>
      )}

      <AddTaskDialog open={dialogOpen} onClose={() => setDialogOpen(false)} />
    </Box>
  );
}
