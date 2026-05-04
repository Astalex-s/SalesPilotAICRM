import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  MenuItem,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import EmptyState from '../components/common/EmptyState';
import { gdprApi } from '../api/gdpr';
import { listUsers } from '../api/users';
import { useLeadStore } from '../store/useLeadStore';
import type { AnonymizeLeadResult, DeleteUserDataResult, GdprAuditEntry } from '../types/gdpr';
import type { User } from '../types/auth';

/* ── Design tokens ── */
const CARD = {
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
  p: 2.5,
};

const SELECT_SX = {
  borderRadius: '10px',
  fontFamily: 'Inter, sans-serif',
  fontSize: 14,
  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E2EAF4' },
  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#CBD5E8' },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00A8E8', borderWidth: 2 },
};

/* ── Confirm dialog ── */
function ConfirmDialog({
  open,
  title,
  desc,
  confirmLabel,
  danger,
  loading,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  desc: string;
  confirmLabel: string;
  danger?: boolean;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: '16px', boxShadow: '0 24px 64px rgba(13,33,68,0.18)' } }}
    >
      <DialogTitle
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          fontSize: 17,
          color: '#0D2144',
          pt: 3,
          px: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
        }}
      >
        <WarningAmberIcon sx={{ color: '#EF4444', fontSize: 22 }} />
        {title}
      </DialogTitle>
      <DialogContent sx={{ px: 3 }}>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#4B6080', lineHeight: 1.6 }}>
          {desc}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3, gap: 1.5 }}>
        <Button
          onClick={onCancel}
          disabled={loading}
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
          {t('gdpr.deleteUser.cancel')}
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          variant="contained"
          startIcon={loading ? <CircularProgress size={14} color="inherit" /> : undefined}
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 14,
            bgcolor: danger ? '#EF4444' : '#00A8E8',
            color: '#fff',
            borderRadius: '10px',
            px: 2.5,
            textTransform: 'none',
            boxShadow: 'none',
            '&:hover': { bgcolor: danger ? '#DC2626' : '#0090CC', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

/* ── Delete result badge ── */
function ResultTag({ label }: { label: string }) {
  return (
    <Box
      sx={{
        display: 'inline-flex',
        px: 1.25,
        py: 0.3,
        borderRadius: '20px',
        bgcolor: 'rgba(239,68,68,0.1)',
        color: '#DC2626',
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
        fontWeight: 600,
        mr: 0.75,
        mb: 0.5,
      }}
    >
      {label}
    </Box>
  );
}

/* ── Delete User Data card ── */
function DeleteUserCard({
  users,
  usersLoading,
  onAction,
}: {
  users: User[];
  usersLoading: boolean;
  onAction: () => void;
}) {
  const { t } = useTranslation();
  const [selectedId, setSelectedId] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DeleteUserDataResult | null>(null);

  const selected = users.find((u) => u.id === selectedId);

  async function handleConfirm() {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await gdprApi.deleteUserData(selectedId);
      setResult(res);
      setConfirmOpen(false);
      setSelectedId('');
      onAction();
    } catch {
      setError(t('gdpr.errors.deleteUser'));
      setConfirmOpen(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box sx={CARD}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: '8px',
            bgcolor: 'rgba(239,68,68,0.1)',
            color: '#EF4444',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <DeleteForeverIcon sx={{ fontSize: 18 }} />
        </Box>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: '#0D2144' }}>
          {t('gdpr.deleteUser.title')}
        </Typography>
      </Box>

      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#94A3B8', lineHeight: 1.5, mb: 2.5 }}>
        {t('gdpr.deleteUser.desc')}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }}>{error}</Alert>}

      {result && (
        <Alert severity="warning" icon={false} sx={{ mb: 2, borderRadius: '10px', bgcolor: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)' }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, fontWeight: 600, color: '#DC2626', mb: 0.75 }}>
            {t('gdpr.deleteUser.successLabel')}
          </Typography>
          <ResultTag label={t('gdpr.deleteUser.successLeads', { count: result.leads_deleted })} />
          <ResultTag label={t('gdpr.deleteUser.successDeals', { count: result.deals_deleted })} />
          <ResultTag label={t('gdpr.deleteUser.successEmails', { count: result.emails_deleted })} />
          <ResultTag label={t('gdpr.deleteUser.successActivities', { count: result.activities_erased })} />
        </Alert>
      )}

      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 500, color: '#4B6080', mb: 0.75 }}>
        {t('gdpr.deleteUser.selectLabel')}
      </Typography>
      <Select
        value={selectedId}
        onChange={(e) => { setSelectedId(e.target.value); setResult(null); }}
        size="small"
        displayEmpty
        fullWidth
        disabled={usersLoading}
        sx={{ ...SELECT_SX, mb: 2 }}
      >
        <MenuItem value="" disabled sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#94A3B8' }}>
          {t('gdpr.deleteUser.selectPlaceholder')}
        </MenuItem>
        {users.map((u) => (
          <MenuItem key={u.id} value={u.id} sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14 }}>
            {u.first_name} {u.last_name} · {u.email}
          </MenuItem>
        ))}
      </Select>

      <Button
        variant="contained"
        startIcon={<DeleteForeverIcon sx={{ fontSize: 18 }} />}
        onClick={() => setConfirmOpen(true)}
        disabled={!selectedId || loading}
        fullWidth
        sx={{
          bgcolor: '#EF4444',
          color: '#fff',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 600,
          fontSize: 14,
          borderRadius: '10px',
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': { bgcolor: '#DC2626', boxShadow: 'none' },
          '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
        }}
      >
        {t('gdpr.deleteUser.button')}
      </Button>

      <ConfirmDialog
        open={confirmOpen}
        title={t('gdpr.deleteUser.confirmTitle')}
        desc={t('gdpr.deleteUser.confirmDesc', {
          name: selected ? `${selected.first_name} ${selected.last_name}` : '',
        })}
        confirmLabel={t('gdpr.deleteUser.confirm')}
        danger
        loading={loading}
        onConfirm={handleConfirm}
        onCancel={() => setConfirmOpen(false)}
      />
    </Box>
  );
}

/* ── Anonymize Lead card ── */
function AnonymizeLeadCard({ onAction }: { onAction: () => void }) {
  const { t } = useTranslation();
  const { leads, fetchLeads } = useLeadStore();

  useEffect(() => { fetchLeads(); }, [fetchLeads]);

  const [selectedId, setSelectedId] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnonymizeLeadResult | null>(null);

  const selected = leads.find((l) => l.id === selectedId);

  async function handleConfirm() {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await gdprApi.anonymizeLead(selectedId);
      setResult(res);
      setConfirmOpen(false);
      setSelectedId('');
      onAction();
    } catch {
      setError(t('gdpr.errors.anonymize'));
      setConfirmOpen(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box sx={CARD}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: '8px',
            bgcolor: 'rgba(245,158,11,0.1)',
            color: '#D97706',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <VisibilityOffIcon sx={{ fontSize: 18 }} />
        </Box>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: '#0D2144' }}>
          {t('gdpr.anonymizeLead.title')}
        </Typography>
      </Box>

      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#94A3B8', lineHeight: 1.5, mb: 2.5 }}>
        {t('gdpr.anonymizeLead.desc')}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }}>{error}</Alert>}

      {result && (
        <Alert severity="warning" icon={false} sx={{ mb: 2, borderRadius: '10px', bgcolor: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)' }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, fontWeight: 600, color: '#D97706', mb: 0.75 }}>
            {t('gdpr.anonymizeLead.successLabel')}
          </Typography>
          <ResultTag label={t('gdpr.anonymizeLead.successEmails', { count: result.emails_deleted })} />
          <ResultTag label={t('gdpr.anonymizeLead.successActivities', { count: result.activities_erased })} />
        </Alert>
      )}

      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 500, color: '#4B6080', mb: 0.75 }}>
        {t('gdpr.anonymizeLead.selectLabel')}
      </Typography>
      <Select
        value={selectedId}
        onChange={(e) => { setSelectedId(e.target.value); setResult(null); }}
        size="small"
        displayEmpty
        fullWidth
        sx={{ ...SELECT_SX, mb: 2 }}
      >
        <MenuItem value="" disabled sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#94A3B8' }}>
          {t('gdpr.anonymizeLead.selectPlaceholder')}
        </MenuItem>
        {leads.map((l) => (
          <MenuItem key={l.id} value={l.id} sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14 }}>
            {l.first_name} {l.last_name}
            {l.company ? ` · ${l.company}` : ''}
            {` · ${l.email}`}
          </MenuItem>
        ))}
      </Select>

      <Button
        variant="contained"
        startIcon={<VisibilityOffIcon sx={{ fontSize: 18 }} />}
        onClick={() => setConfirmOpen(true)}
        disabled={!selectedId || loading}
        fullWidth
        sx={{
          bgcolor: '#F59E0B',
          color: '#fff',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 600,
          fontSize: 14,
          borderRadius: '10px',
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': { bgcolor: '#D97706', boxShadow: 'none' },
          '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
        }}
      >
        {t('gdpr.anonymizeLead.button')}
      </Button>

      <ConfirmDialog
        open={confirmOpen}
        title={t('gdpr.anonymizeLead.confirmTitle')}
        desc={t('gdpr.anonymizeLead.confirmDesc', {
          name: selected ? `${selected.first_name} ${selected.last_name}` : '',
        })}
        confirmLabel={t('gdpr.anonymizeLead.confirm')}
        loading={loading}
        onConfirm={handleConfirm}
        onCancel={() => setConfirmOpen(false)}
      />
    </Box>
  );
}

/* ── Audit Log table ── */
function AuditLogCard({ entries, loading, error }: { entries: GdprAuditEntry[]; loading: boolean; error: string | null }) {
  const { t } = useTranslation();

  return (
    <Box sx={{ background: '#FFFFFF', border: '1px solid #E2EAF4', borderRadius: '16px', boxShadow: '0 4px 24px rgba(13,33,68,0.07)' }}>
      <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: '#0D2144' }}>
          {t('gdpr.auditLog.title')}
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mx: 2.5, mb: 1.5, borderRadius: '10px' }}>{error}</Alert>}

      <Table sx={{ tableLayout: 'fixed' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: '#F8FAFC' }}>
            {[
              { label: t('gdpr.auditLog.eventType'), width: '16%' },
              { label: t('gdpr.auditLog.targetType'), width: '12%' },
              { label: t('gdpr.auditLog.summary'), width: undefined },
              { label: t('gdpr.auditLog.date'), width: '14%' },
            ].map(({ label, width }, i) => (
              <TableCell
                key={i}
                sx={{
                  width,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  px: i === 0 ? 2.5 : 2,
                }}
              >
                {label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>

        <TableBody>
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <TableRow key={i} sx={{ height: 52 }}>
                {Array.from({ length: 4 }).map((__, j) => (
                  <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                    <Skeleton variant="text" width="80%" />
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : entries.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} sx={{ border: 'none' }}>
                <EmptyState
                  icon="shield"
                  title={t('gdpr.auditLog.empty')}
                  subtitle={t('gdpr.auditLog.emptySubtitle')}
                  compact
                />
              </TableCell>
            </TableRow>
          ) : (
            entries.map((entry) => {
              const isDelete = entry.event_type === 'user_data_deleted';
              return (
                <TableRow
                  key={entry.id}
                  sx={{
                    height: 52,
                    '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                    '&:hover': { bgcolor: '#F0F5FF' },
                  }}
                >
                  <TableCell sx={{ py: 1, px: 2.5 }}>
                    <Box
                      sx={{
                        display: 'inline-flex',
                        px: 1.25,
                        py: 0.3,
                        borderRadius: '20px',
                        bgcolor: isDelete ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                        color: isDelete ? '#DC2626' : '#D97706',
                        fontFamily: 'Inter, sans-serif',
                        fontSize: 11,
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {t(`gdpr.auditLog.events.${entry.event_type}`)}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ py: 1, px: 2 }}>
                    <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', textTransform: 'capitalize' }}>
                      {entry.target_type}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ py: 1, px: 2 }}>
                    <Typography noWrap sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#4B6080' }}>
                      {entry.summary}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ py: 1, px: 2 }}>
                    <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>
                      {new Date(entry.performed_at).toLocaleDateString(undefined, {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </Typography>
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </Box>
  );
}

/* ── Main page ── */
export default function GdprPage() {
  const { t } = useTranslation();

  const [users, setUsers] = useState<User[]>([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [auditEntries, setAuditEntries] = useState<GdprAuditEntry[]>([]);
  const [auditLoading, setAuditLoading] = useState(true);
  const [auditError, setAuditError] = useState<string | null>(null);

  async function loadUsers() {
    try {
      const data = await listUsers();
      setUsers(data);
    } catch {
      // users list failure is non-critical
    } finally {
      setUsersLoading(false);
    }
  }

  async function loadAuditLog() {
    setAuditLoading(true);
    setAuditError(null);
    try {
      const data = await gdprApi.getAuditLog();
      setAuditEntries(data.entries);
    } catch {
      setAuditError(t('gdpr.errors.auditLog'));
    } finally {
      setAuditLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
    loadAuditLog();
  }, []);

  return (
    <Box>
      {/* ── Header ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 24,
            fontWeight: 700,
            color: '#0D2144',
          }}
        >
          {t('gdpr.title')}
        </Typography>
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 0.5,
            px: 1.25,
            py: 0.4,
            borderRadius: '20px',
            bgcolor: 'rgba(239,68,68,0.1)',
            color: '#DC2626',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          <LockIcon sx={{ fontSize: 12 }} />
          {t('gdpr.adminOnly')}
        </Box>
      </Box>

      {/* ── Warning banner ── */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          p: '12px 16px',
          mb: 3,
          borderRadius: '12px',
          bgcolor: 'rgba(239,68,68,0.06)',
          border: '1px solid rgba(239,68,68,0.2)',
        }}
      >
        <WarningAmberIcon sx={{ color: '#EF4444', flexShrink: 0 }} />
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#DC2626', fontWeight: 500 }}>
          {t('gdpr.warning')}
        </Typography>
      </Box>

      {/* ── Action cards ── */}
      <Grid container spacing={2.5} sx={{ mb: 2.5 }}>
        <Grid item xs={12} md={6}>
          <DeleteUserCard
            users={users}
            usersLoading={usersLoading}
            onAction={loadAuditLog}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <AnonymizeLeadCard onAction={loadAuditLog} />
        </Grid>
      </Grid>

      <Divider sx={{ borderColor: '#E2EAF4', mb: 2.5 }} />

      {/* ── Audit log ── */}
      <AuditLogCard
        entries={auditEntries}
        loading={auditLoading}
        error={auditError}
      />
    </Box>
  );
}
