import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { leadsApi } from '../../api/leads';
import { useAuthStore } from '../../store/useAuthStore';
import { type Lead, type LeadSource } from '../../types/lead';

const SOURCES: LeadSource[] = [
  'website', 'referral', 'cold_call', 'social_media', 'email_campaign', 'other',
];

interface AddLeadDialogProps {
  open: boolean;
  onClose: () => void;
  onLeadCreated: (lead: Lead) => void;
}

export default function AddLeadDialog({ open, onClose, onLeadCreated }: AddLeadDialogProps) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [company, setCompany] = useState('');
  const [source, setSource] = useState<LeadSource>('website');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClose = () => {
    if (submitting) return;
    setFirstName('');
    setLastName('');
    setEmail('');
    setPhone('');
    setCompany('');
    setSource('website');
    setError(null);
    onClose();
  };

  const handleSubmit = async () => {
    if (!firstName.trim() || !lastName.trim() || !email.trim()) {
      setError(t('leads.dialog.validationRequired'));
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const lead = await leadsApi.create({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        company: company.trim() || undefined,
        source,
        owner_id: user?.id ?? '',
      });
      onLeadCreated(lead);
      handleClose();
    } catch {
      setError(t('leads.dialog.submitError'));
    } finally {
      setSubmitting(false);
    }
  };

  const inputSx = {
    '& .MuiInputBase-root': { fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' },
    '& label': { fontFamily: 'Inter', fontSize: 13 },
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: { borderRadius: '16px', boxShadow: '0 8px 40px rgba(13,33,68,0.12)', overflow: 'hidden' },
      }}
    >
      {/* Header */}
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        px: 3, py: 2, borderBottom: '1px solid #E8EFF7',
      }}>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 16, color: '#0D2144' }}>
          {t('leads.dialog.title')}
        </Typography>
        <Box
          onClick={handleClose}
          sx={{ cursor: submitting ? 'default' : 'pointer', color: '#94A3B8', display: 'flex', '&:hover': { color: '#0D2144' } }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6L6 18 M6 6l12 12" />
          </svg>
        </Box>
      </Box>

      <DialogContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 1.5 }}>
            <TextField
              size="small" label={t('leads.dialog.firstName')} value={firstName}
              onChange={(e) => setFirstName(e.target.value)} fullWidth sx={inputSx}
            />
            <TextField
              size="small" label={t('leads.dialog.lastName')} value={lastName}
              onChange={(e) => setLastName(e.target.value)} fullWidth sx={inputSx}
            />
          </Box>

          <TextField
            size="small" label={t('leads.dialog.email')} type="email" value={email}
            onChange={(e) => setEmail(e.target.value)} fullWidth sx={inputSx}
          />

          <TextField
            size="small" label={t('leads.dialog.phone')} value={phone}
            onChange={(e) => setPhone(e.target.value)} fullWidth sx={inputSx}
          />

          <TextField
            size="small" label={t('leads.dialog.company')} value={company}
            onChange={(e) => setCompany(e.target.value)} fullWidth sx={inputSx}
          />

          <FormControl size="small" fullWidth>
            <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('leads.dialog.source')}</InputLabel>
            <Select
              value={source}
              label={t('leads.dialog.source')}
              onChange={(e) => setSource(e.target.value as LeadSource)}
              sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
            >
              {SOURCES.map((s) => (
                <MenuItem key={s} value={s} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                  {t(`leads.source.${s}`)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {error && (
            <Alert
              severity="error"
              sx={{ borderRadius: '8px', py: 0.5, '& .MuiAlert-message': { fontFamily: 'Inter', fontSize: 12 } }}
            >
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end', pt: 0.5 }}>
            <Button
              variant="outlined"
              onClick={handleClose}
              disabled={submitting}
              sx={{
                fontFamily: 'Inter', fontSize: 13, fontWeight: 500, textTransform: 'none',
                borderColor: '#E8EFF7', color: '#64748B', borderRadius: '10px',
                '&:hover': { borderColor: '#CBD5E8', bgcolor: 'transparent' },
              }}
            >
              {t('leads.dialog.cancel')}
            </Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting}
              sx={{
                bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
                fontSize: 13, borderRadius: '10px', textTransform: 'none', boxShadow: 'none',
                minWidth: 130,
                '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
                '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
              }}
            >
              {submitting
                ? <><CircularProgress size={14} sx={{ color: '#fff', mr: 1 }} />{t('leads.dialog.submitting')}</>
                : t('leads.dialog.submit')
              }
            </Button>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
