import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMeetingStore } from '../../store/useMeetingStore';

interface Props {
  open: boolean;
  onClose: () => void;
  defaultDate?: string; // yyyy-MM-dd
}

function toLocalDatetimeValue(date?: string): string {
  if (!date) return '';
  // yyyy-MM-dd → yyyy-MM-ddTHH:mm (local noon)
  return `${date}T09:00`;
}

export default function AddMeetingDialog({ open, onClose, defaultDate }: Props) {
  const { t } = useTranslation();
  const { createMeeting } = useMeetingStore();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startTime, setStartTime] = useState(() => toLocalDatetimeValue(defaultDate));
  const [endTime, setEndTime] = useState('');
  const [location, setLocation] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleClose = () => {
    setTitle('');
    setDescription('');
    setStartTime(toLocalDatetimeValue(defaultDate));
    setEndTime('');
    setLocation('');
    setError('');
    onClose();
  };

  const handleSubmit = async () => {
    if (!title.trim()) { setError(t('calendar.dialog.titleRequired')); return; }
    if (!startTime) { setError(t('calendar.dialog.startRequired')); return; }
    setSaving(true);
    setError('');
    try {
      await createMeeting({
        title: title.trim(),
        description: description.trim() || null,
        start_time: new Date(startTime).toISOString(),
        end_time: endTime ? new Date(endTime).toISOString() : null,
        location: location.trim() || null,
      });
      handleClose();
    } catch {
      setError(t('calendar.dialog.saveFailed'));
    } finally {
      setSaving(false);
    }
  };

  const inputSx = {
    '& .MuiOutlinedInput-root': {
      fontFamily: 'Inter, sans-serif',
      fontSize: 14,
      borderRadius: '10px',
    },
    '& label': { fontFamily: 'Inter, sans-serif', fontSize: 14 },
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: '16px', p: 1 } }}
    >
      <DialogTitle sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 18, pb: 0 }}>
        {t('calendar.dialog.title')}
      </DialogTitle>
      <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label={t('calendar.dialog.titleLabel')}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          fullWidth
          required
          sx={inputSx}
        />
        <TextField
          label={t('calendar.dialog.description')}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          fullWidth
          multiline
          rows={2}
          sx={inputSx}
        />
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <TextField
            label={t('calendar.dialog.startTime')}
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
            sx={inputSx}
          />
          <TextField
            label={t('calendar.dialog.endTime')}
            type="datetime-local"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            fullWidth
            InputLabelProps={{ shrink: true }}
            sx={inputSx}
          />
        </Box>
        <TextField
          label={t('calendar.dialog.location')}
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          fullWidth
          sx={inputSx}
        />

        {error && (
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#EF4444' }}>
            {error}
          </Typography>
        )}

        <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end', pt: 1 }}>
          <Button
            onClick={handleClose}
            sx={{ fontFamily: 'Inter, sans-serif', textTransform: 'none', color: '#5E6E82' }}
          >
            {t('calendar.dialog.cancel')}
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={saving}
            sx={{
              bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter, sans-serif',
              fontWeight: 600, textTransform: 'none', borderRadius: '10px',
              boxShadow: 'none', '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            }}
          >
            {saving ? <CircularProgress size={18} sx={{ color: '#fff' }} /> : t('calendar.dialog.save')}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
