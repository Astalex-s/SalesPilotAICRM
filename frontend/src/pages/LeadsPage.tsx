import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import EmptyState from '../components/common/EmptyState';
import CsvImportDialog from '../components/leads/CsvImportDialog';
import { useAuthStore } from '../store/useAuthStore';
import { useLeadStore } from '../store/useLeadStore';
import { type Lead, type LeadSource, type LeadStatus } from '../types/lead';

/* ── Design tokens ── */
const CARD = {
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
  overflowX: 'auto' as const,
};

/* ── Avatar helpers ── */
const AVATAR_PALETTE = ['#00A8E8', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#0D2144'];

function avatarColor(name: string) {
  return AVATAR_PALETTE[name.charCodeAt(0) % AVATAR_PALETTE.length];
}

function initials(lead: Lead) {
  return `${lead.first_name[0] ?? ''}${lead.last_name[0] ?? ''}`.toUpperCase();
}

/* ── Status badge ── */
const STATUS_STYLE: Record<LeadStatus, { bg: string; color: string }> = {
  new:         { bg: 'rgba(0,168,232,0.12)',  color: '#0090CC' },
  contacted:   { bg: 'rgba(245,158,11,0.12)', color: '#D97706' },
  qualified:   { bg: 'rgba(16,185,129,0.12)', color: '#059669' },
  unqualified: { bg: 'rgba(239,68,68,0.12)',  color: '#DC2626' },
  converted:   { bg: 'rgba(13,33,68,0.10)',   color: '#0D2144' },
};

function StatusBadge({ status }: { status: LeadStatus }) {
  const { t } = useTranslation();
  const s = STATUS_STYLE[status];
  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        px: 1.25,
        py: 0.4,
        borderRadius: '20px',
        bgcolor: s.bg,
        color: s.color,
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      {t(`leads.status.${status}`)}
    </Box>
  );
}

/* ── Source label ── */
function SourceLabel({ source }: { source: string }) {
  const { t } = useTranslation();
  return (
    <Typography sx={{ fontSize: 13, color: '#4B6080', fontFamily: 'Inter, sans-serif' }}>
      {t(`leads.source.${source}`, source)}
    </Typography>
  );
}

/* ── Filter pills ── */
const FILTER_OPTIONS: Array<LeadStatus | 'all'> = [
  'all', 'new', 'contacted', 'qualified', 'unqualified', 'converted',
];

/* ── Pagination ── */
const PAGE_SIZE = 20;

/* ── Skeleton rows ── */
function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <TableRow key={i} sx={{ height: 56 }}>
          <TableCell><Skeleton variant="circular" width={36} height={36} /></TableCell>
          <TableCell><Skeleton variant="text" width={160} /></TableCell>
          <TableCell><Skeleton variant="text" width={120} /></TableCell>
          <TableCell><Skeleton variant="rounded" width={80} height={24} sx={{ borderRadius: '20px' }} /></TableCell>
          <TableCell><Skeleton variant="text" width={100} /></TableCell>
          <TableCell><Skeleton variant="text" width={80} /></TableCell>
        </TableRow>
      ))}
    </>
  );
}

/* ── Source options ── */
const SOURCES: LeadSource[] = [
  'website', 'referral', 'cold_call', 'social_media', 'email_campaign', 'other',
];

const INPUT_SX = {
  '& .MuiOutlinedInput-root': {
    borderRadius: '10px',
    fontFamily: 'Inter, sans-serif',
    fontSize: 14,
    '& fieldset': { borderColor: '#E2EAF4' },
    '&:hover fieldset': { borderColor: '#CBD5E8' },
    '&.Mui-focused fieldset': { borderColor: '#00A8E8', borderWidth: 2 },
  },
  '& .MuiInputLabel-root': {
    fontFamily: 'Inter, sans-serif',
    fontSize: 14,
    '&.Mui-focused': { color: '#00A8E8' },
  },
};

/* ── Add Lead Dialog ── */
interface AddLeadDialogProps {
  open: boolean;
  onClose: () => void;
}

function AddLeadDialog({ open, onClose }: AddLeadDialogProps) {
  const { t } = useTranslation();
  const { createLead } = useLeadStore();
  const user = useAuthStore((s) => s.user);

  const emptyForm = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company: '',
    source: 'other' as LeadSource,
  };

  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function set(field: keyof typeof emptyForm, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setFormError(null);
  }

  async function handleSubmit() {
    if (!form.first_name.trim() || !form.last_name.trim() || !form.email.trim()) {
      setFormError(t('leads.dialog.validationRequired'));
      return;
    }
    if (!user) return;

    setSubmitting(true);
    try {
      await createLead({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || undefined,
        company: form.company.trim() || undefined,
        source: form.source,
        owner_id: user.id,
      });
      setForm(emptyForm);
      onClose();
    } catch {
      setFormError(t('leads.dialog.submitError'));
    } finally {
      setSubmitting(false);
    }
  }

  function handleClose() {
    setForm(emptyForm);
    setFormError(null);
    onClose();
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '20px',
          boxShadow: '0 24px 64px rgba(13,33,68,0.18)',
        },
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          fontSize: 18,
          color: '#0D2144',
          px: 3,
          pt: 3,
          pb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {t('leads.dialog.title')}
        <IconButton onClick={handleClose} size="small" sx={{ color: '#94A3B8' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Divider sx={{ borderColor: '#E2EAF4' }} />

      <DialogContent sx={{ px: 3, py: 3 }}>
        {formError && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: '10px' }}>
            {formError}
          </Alert>
        )}

        {/* Name row */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label={t('leads.dialog.firstName')}
            value={form.first_name}
            onChange={(e) => set('first_name', e.target.value)}
            fullWidth
            size="small"
            sx={INPUT_SX}
          />
          <TextField
            label={t('leads.dialog.lastName')}
            value={form.last_name}
            onChange={(e) => set('last_name', e.target.value)}
            fullWidth
            size="small"
            sx={INPUT_SX}
          />
        </Box>

        {/* Email */}
        <TextField
          label={t('leads.dialog.email')}
          type="email"
          value={form.email}
          onChange={(e) => set('email', e.target.value)}
          fullWidth
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        {/* Phone */}
        <TextField
          label={t('leads.dialog.phone')}
          value={form.phone}
          onChange={(e) => set('phone', e.target.value)}
          fullWidth
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        {/* Company */}
        <TextField
          label={t('leads.dialog.company')}
          value={form.company}
          onChange={(e) => set('company', e.target.value)}
          fullWidth
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        {/* Source */}
        <Box sx={{ mb: 3 }}>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 12,
              fontWeight: 500,
              color: '#4B6080',
              mb: 0.75,
            }}
          >
            {t('leads.dialog.source')}
          </Typography>
          <Select
            value={form.source}
            onChange={(e) => set('source', e.target.value)}
            size="small"
            fullWidth
            sx={{
              borderRadius: '10px',
              fontFamily: 'Inter, sans-serif',
              fontSize: 14,
              '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E2EAF4' },
              '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#CBD5E8' },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#00A8E8',
                borderWidth: 2,
              },
            }}
          >
            {SOURCES.map((s) => (
              <MenuItem
                key={s}
                value={s}
                sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14 }}
              >
                {t(`leads.source.${s}`)}
              </MenuItem>
            ))}
          </Select>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end' }}>
          <Button
            onClick={handleClose}
            disabled={submitting}
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              color: '#4B6080',
              borderRadius: '10px',
              border: '1px solid #E2EAF4',
              px: 2.5,
              textTransform: 'none',
              '&:hover': { bgcolor: '#F0F5FF' },
            }}
          >
            {t('leads.dialog.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            variant="contained"
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              bgcolor: '#00A8E8',
              color: '#fff',
              borderRadius: '10px',
              px: 2.5,
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
              '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
            }}
          >
            {submitting ? t('leads.dialog.submitting') : t('leads.dialog.submit')}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

/* ── Main page ── */
export default function LeadsPage() {
  const { t } = useTranslation();
  const { leads, loading, error, fetchLeads } = useLeadStore();
  const navigate = useNavigate();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [csvImportOpen, setCsvImportOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<LeadStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);

  useEffect(() => { fetchLeads(); }, [fetchLeads]);

  // Reset page when filters change
  useEffect(() => { setPage(0); }, [statusFilter, search]);

  const filtered = useMemo(() => {
    return leads.filter((lead) => {
      if (statusFilter !== 'all' && lead.status !== statusFilter) return false;
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          lead.first_name.toLowerCase().includes(q) ||
          lead.last_name.toLowerCase().includes(q) ||
          lead.email.toLowerCase().includes(q) ||
          (lead.company ?? '').toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [leads, statusFilter, search]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const from = filtered.length === 0 ? 0 : page * PAGE_SIZE + 1;
  const to = Math.min((page + 1) * PAGE_SIZE, filtered.length);

  return (
    <Box>
      {/* ── Page header ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 24,
              fontWeight: 700,
              color: '#0D2144',
            }}
          >
            {t('leads.title')}
          </Typography>
          {!loading && (
            <Box
              sx={{
                px: 1.5,
                py: 0.25,
                borderRadius: '20px',
                bgcolor: '#E8F4FF',
                color: '#00A8E8',
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                fontWeight: 600,
              }}
            >
              {t('leads.count', { count: filtered.length })}
            </Box>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="outlined"
            onClick={() => setCsvImportOpen(true)}
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              color: '#0D2144',
              borderColor: '#E2EAF4',
              borderRadius: '10px',
              px: 2.5,
              textTransform: 'none',
              '&:hover': { borderColor: '#00A8E8', color: '#00A8E8', bgcolor: 'rgba(0,168,232,0.04)' },
            }}
          >
            {t('leads.csvImport.button')}
          </Button>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{
            bgcolor: '#00A8E8',
            color: '#fff',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 14,
            borderRadius: '10px',
            px: 2.5,
            textTransform: 'none',
            boxShadow: 'none',
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
          }}
        >
          {t('leads.addLead')}
        </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      {/* ── Toolbar: search + filter pills ── */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          mb: 2.5,
          flexWrap: 'wrap',
        }}
      >
        {/* Search */}
        <TextField
          size="small"
          placeholder={t('leads.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#94A3B8', fontSize: 18 }} />
              </InputAdornment>
            ),
          }}
          sx={{
            width: 280,
            '& .MuiOutlinedInput-root': {
              borderRadius: '10px',
              bgcolor: '#FFFFFF',
              fontFamily: 'Inter, sans-serif',
              fontSize: 14,
              '& fieldset': { borderColor: '#E2EAF4' },
              '&:hover fieldset': { borderColor: '#CBD5E8' },
              '&.Mui-focused fieldset': { borderColor: '#00A8E8', borderWidth: 2 },
            },
          }}
        />

        {/* Status filter pills */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {FILTER_OPTIONS.map((opt) => {
            const active = statusFilter === opt;
            return (
              <Box
                key={opt}
                onClick={() => setStatusFilter(opt)}
                sx={{
                  px: 1.75,
                  py: 0.6,
                  borderRadius: '20px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  fontWeight: active ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  bgcolor: active ? '#00A8E8' : '#FFFFFF',
                  color: active ? '#FFFFFF' : '#4B6080',
                  border: `1px solid ${active ? '#00A8E8' : '#E2EAF4'}`,
                  '&:hover': {
                    bgcolor: active ? '#0090CC' : '#F0F5FF',
                    borderColor: active ? '#0090CC' : '#CBD5E8',
                  },
                }}
              >
                {opt === 'all' ? t('leads.filterAll') : t(`leads.status.${opt}`)}
              </Box>
            );
          })}
        </Box>
      </Box>

      <AddLeadDialog open={dialogOpen} onClose={() => setDialogOpen(false)} />

      <CsvImportDialog
        open={csvImportOpen}
        onClose={() => setCsvImportOpen(false)}
        onImported={fetchLeads}
      />

      {/* ── Table card ── */}
      <Box sx={CARD}>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {/* Avatar col */}
              <TableCell sx={{ width: 52, border: 'none', py: 1.5 }} />
              <TableCell
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                }}
              >
                {t('leads.table.name')}
              </TableCell>
              <TableCell
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  width: '18%',
                }}
              >
                {t('leads.table.company')}
              </TableCell>
              <TableCell
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  width: '14%',
                }}
              >
                {t('leads.table.status')}
              </TableCell>
              <TableCell
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  width: '16%',
                }}
              >
                {t('leads.table.source')}
              </TableCell>
              <TableCell
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  width: '12%',
                }}
              >
                {t('leads.table.created')}
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              <SkeletonRows />
            ) : paginated.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ border: 'none' }}>
                  {leads.length === 0 ? (
                    <EmptyState
                      icon="leads"
                      title={t('leads.noLeads')}
                      subtitle={t('leads.noLeadsSubtitle')}
                      action={{ label: t('leads.addLead'), onClick: () => setDialogOpen(true) }}
                    />
                  ) : (
                    <EmptyState
                      icon="search"
                      title={t('leads.noResults')}
                      subtitle={t('leads.noResultsSubtitle')}
                    />
                  )}
                </TableCell>
              </TableRow>
            ) : (
              paginated.map((lead) => {
                const color = avatarColor(lead.first_name);
                const createdDate = new Date(lead.created_at).toLocaleDateString(undefined, {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                });

                return (
                  <TableRow
                    key={lead.id}
                    onClick={() => navigate(`/leads/${lead.id}`)}
                    sx={{
                      height: 56,
                      cursor: 'pointer',
                      transition: 'background 0.12s',
                      '&:hover': { bgcolor: '#F0F5FF' },
                      '& td': {
                        border: 'none',
                        borderTop: '1px solid #F0F5FF',
                      },
                    }}
                  >
                    {/* Avatar */}
                    <TableCell sx={{ py: 1, pl: 2 }}>
                      <Box
                        sx={{
                          width: 36,
                          height: 36,
                          borderRadius: '50%',
                          bgcolor: color,
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontFamily: 'Inter, sans-serif',
                          fontSize: 13,
                          fontWeight: 700,
                          flexShrink: 0,
                        }}
                      >
                        {initials(lead)}
                      </Box>
                    </TableCell>

                    {/* Name + email */}
                    <TableCell sx={{ py: 1 }}>
                      <Typography
                        sx={{
                          fontFamily: 'Inter, sans-serif',
                          fontWeight: 600,
                          fontSize: 14,
                          color: '#0D2144',
                          lineHeight: 1.3,
                        }}
                      >
                        {lead.first_name} {lead.last_name}
                      </Typography>
                      <Typography
                        sx={{
                          fontFamily: 'Inter, sans-serif',
                          fontSize: 12,
                          color: '#94A3B8',
                          lineHeight: 1.3,
                        }}
                      >
                        {lead.email}
                      </Typography>
                    </TableCell>

                    {/* Company */}
                    <TableCell sx={{ py: 1 }}>
                      {lead.company ? (
                        <Typography
                          sx={{
                            fontFamily: 'Inter, sans-serif',
                            fontSize: 13,
                            color: '#4B6080',
                            fontWeight: 500,
                          }}
                        >
                          {lead.company}
                        </Typography>
                      ) : (
                        <Typography sx={{ fontSize: 13, color: '#CBD5E8' }}>—</Typography>
                      )}
                    </TableCell>

                    {/* Status */}
                    <TableCell sx={{ py: 1 }}>
                      <StatusBadge status={lead.status} />
                    </TableCell>

                    {/* Source */}
                    <TableCell sx={{ py: 1 }}>
                      <SourceLabel source={lead.source} />
                    </TableCell>

                    {/* Created */}
                    <TableCell sx={{ py: 1 }}>
                      <Typography
                        sx={{
                          fontFamily: 'Inter, sans-serif',
                          fontSize: 13,
                          color: '#94A3B8',
                        }}
                      >
                        {createdDate}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* ── Pagination footer ── */}
        {!loading && filtered.length > 0 && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              px: 3,
              py: 2,
              borderTop: '1px solid #F0F5FF',
            }}
          >
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#94A3B8' }}>
              {t('leads.pagination.showing', { from, to, total: filtered.length })}
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                sx={{
                  px: 1.5,
                  py: 0.5,
                  borderRadius: '8px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: page === 0 ? 'not-allowed' : 'pointer',
                  color: page === 0 ? '#CBD5E8' : '#4B6080',
                  border: '1px solid #E2EAF4',
                  bgcolor: '#FFFFFF',
                  userSelect: 'none',
                  '&:hover': page === 0 ? {} : { bgcolor: '#F0F5FF' },
                }}
              >
                ←
              </Box>

              {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
                const p = i;
                return (
                  <Box
                    key={p}
                    onClick={() => setPage(p)}
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 13,
                      fontWeight: page === p ? 700 : 500,
                      cursor: 'pointer',
                      bgcolor: page === p ? '#00A8E8' : '#FFFFFF',
                      color: page === p ? '#FFFFFF' : '#4B6080',
                      border: `1px solid ${page === p ? '#00A8E8' : '#E2EAF4'}`,
                      userSelect: 'none',
                      '&:hover': { bgcolor: page === p ? '#0090CC' : '#F0F5FF' },
                    }}
                  >
                    {p + 1}
                  </Box>
                );
              })}

              <Box
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                sx={{
                  px: 1.5,
                  py: 0.5,
                  borderRadius: '8px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer',
                  color: page >= totalPages - 1 ? '#CBD5E8' : '#4B6080',
                  border: '1px solid #E2EAF4',
                  bgcolor: '#FFFFFF',
                  userSelect: 'none',
                  '&:hover': page >= totalPages - 1 ? {} : { bgcolor: '#F0F5FF' },
                }}
              >
                →
              </Box>
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
}
