import CloseIcon from '@mui/icons-material/Close';
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/useAuthStore';
import { useTaskStore } from '../../store/useTaskStore';

interface Props {
  open: boolean;
  onClose: () => void;
  leadId?: string;
  dealId?: string;
}

const INPUT_SX = {
  '& .MuiOutlinedInput-root': {
    borderRadius: '10px',
    fontFamily: 'Inter, sans-serif',
    fontSize: 14,
    '& fieldset': { borderColor: 'divider' },
    '&:hover fieldset': { borderColor: '#CBD5E8' },
    '&.Mui-focused fieldset': { borderColor: '#00A8E8', borderWidth: 2 },
  },
  '& .MuiInputLabel-root': {
    fontFamily: 'Inter, sans-serif',
    fontSize: 14,
    '&.Mui-focused': { color: '#00A8E8' },
  },
};

export default function AddTaskDialog({ open, onClose, leadId, dealId }: Props) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const { createTask } = useTaskStore();

  const emptyForm = { title: '', description: '', due_date: '' };
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setField(field: keyof typeof emptyForm, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError(null);
  }

  const handleClose = () => {
    setForm(emptyForm);
    setError(null);
    onClose();
  };

  async function handleSubmit() {
    if (!form.title.trim()) {
      setError(t('tasks.dialog.validationRequired'));
      return;
    }
    if (!user) return;
    setSubmitting(true);
    try {
      await createTask({
        title: form.title.trim(),
        description: form.description.trim() || null,
        due_date: form.due_date || null,
        assignee_id: user.id,
        lead_id: leadId ?? null,
        deal_id: dealId ?? null,
      });
      handleClose();
    } catch {
      setError(t('tasks.dialog.submitError'));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: '16px' } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 16, color: 'text.primary' }}>
        {t('tasks.dialog.title')}
        <IconButton size="small" onClick={handleClose}><CloseIcon fontSize="small" /></IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 1 }}>
        {error && (
          <Typography sx={{ color: '#DC2626', fontSize: 13, fontFamily: 'Inter, sans-serif', mb: 1.5 }}>
            {error}
          </Typography>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 0.5 }}>
          <TextField
            label={t('tasks.dialog.titleField')}
            value={form.title}
            onChange={(e) => setField('title', e.target.value)}
            fullWidth
            size="small"
            sx={INPUT_SX}
          />
          <TextField
            label={t('tasks.dialog.description')}
            value={form.description}
            onChange={(e) => setField('description', e.target.value)}
            fullWidth
            multiline
            minRows={2}
            size="small"
            sx={INPUT_SX}
          />
          <TextField
            label={t('tasks.dialog.dueDate')}
            type="datetime-local"
            value={form.due_date}
            onChange={(e) => setField('due_date', e.target.value)}
            fullWidth
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={INPUT_SX}
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end', mt: 3 }}>
          <Button
            onClick={handleClose}
            disabled={submitting}
            sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14, color: 'text.secondary', borderRadius: '10px', border: '1px solid', borderColor: 'divider', px: 2.5, textTransform: 'none', '&:hover': { bgcolor: 'action.hover' } }}
          >
            {t('tasks.dialog.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            variant="contained"
            sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14, bgcolor: '#00A8E8', color: '#fff', borderRadius: '10px', px: 2.5, textTransform: 'none', boxShadow: 'none', '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' }, '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' } }}
          >
            {submitting ? <CircularProgress size={18} sx={{ color: '#fff' }} /> : t('tasks.dialog.submit')}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
