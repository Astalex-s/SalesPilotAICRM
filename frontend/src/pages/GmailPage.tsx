import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import CloseIcon from '@mui/icons-material/Close';
import CreateIcon from '@mui/icons-material/Create';
import InboxIcon from '@mui/icons-material/Inbox';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import SendIcon from '@mui/icons-material/Send';
import SyncIcon from '@mui/icons-material/Sync';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Collapse,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import EmptyState from '../components/common/EmptyState';
import { gmailApi } from '../api/gmail';
import { useAuthStore } from '../store/useAuthStore';
import { useLeadStore } from '../store/useLeadStore';
import type {
  EmailDirection,
  EmailMessage,
  EmailThreadDetail,
  EmailThreadSummary,
  SendEmailPayload,
} from '../types/email';

/* ── Design tokens ── */
const CARD = {
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

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

/* ── Not-connected card ── */
function ConnectCard({
  onConnect,
  connecting,
  awaitingAuth,
  onRefreshStatus,
  error,
}: {
  onConnect: () => void;
  connecting: boolean;
  awaitingAuth: boolean;
  onRefreshStatus: () => void;
  error: string | null;
}) {
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
      }}
    >
      <Box
        sx={{
          ...CARD,
          maxWidth: 480,
          width: '100%',
          p: 4,
          textAlign: 'center',
        }}
      >
        {/* Gmail icon */}
        <Box
          sx={{
            width: 64,
            height: 64,
            borderRadius: '16px',
            bgcolor: 'rgba(0,168,232,0.1)',
            color: '#00A8E8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2.5,
          }}
        >
          <InboxIcon sx={{ fontSize: 32 }} />
        </Box>

        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 20,
            color: '#0D2144',
            mb: 1,
          }}
        >
          {t('gmail.title')}
        </Typography>

        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 14,
            color: '#94A3B8',
            lineHeight: 1.6,
            mb: 3,
          }}
        >
          {awaitingAuth ? t('gmail.oauthHint') : t('gmail.connectDesc')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: '10px', textAlign: 'left' }}>
            {error}
          </Alert>
        )}

        {awaitingAuth ? (
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={onRefreshStatus}
            disabled={connecting}
            sx={{
              bgcolor: '#10B981',
              color: '#fff',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              borderRadius: '10px',
              px: 3,
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': { bgcolor: '#059669', boxShadow: 'none' },
            }}
          >
            {t('gmail.refreshStatus')}
          </Button>
        ) : (
          <Button
            variant="contained"
            startIcon={connecting ? <CircularProgress size={16} color="inherit" /> : <InboxIcon />}
            onClick={onConnect}
            disabled={connecting}
            sx={{
              bgcolor: '#00A8E8',
              color: '#fff',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              borderRadius: '10px',
              px: 3,
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
              '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
            }}
          >
            {t('gmail.connect')}
          </Button>
        )}
      </Box>
    </Box>
  );
}

/* ── Compose dialog ── */
interface ComposeDialogProps {
  open: boolean;
  onClose: () => void;
  onSent: (msg: EmailMessage) => void;
  userId: string;
}

function ComposeDialog({ open, onClose, onSent, userId }: ComposeDialogProps) {
  const { t } = useTranslation();
  const { leads } = useLeadStore();

  const empty = { to: '', subject: '', body: '', leadId: '' };
  const [form, setForm] = useState(empty);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);

  function set(field: keyof typeof empty, value: string) {
    setForm((p) => ({ ...p, [field]: value }));
    setSendError(null);
  }

  function handleClose() {
    setForm(empty);
    setSendError(null);
    onClose();
  }

  async function handleSend() {
    if (!form.to.trim() || !form.subject.trim() || !form.body.trim()) return;
    setSending(true);
    try {
      const payload: SendEmailPayload = {
        to: form.to.trim(),
        subject: form.subject.trim(),
        body: form.body.trim(),
        performed_by_id: userId,
        ...(form.leadId ? { lead_id: form.leadId } : {}),
      };
      const msg = await gmailApi.sendEmail(payload);
      onSent(msg);
      handleClose();
    } catch {
      setSendError(t('gmail.errors.send'));
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: '20px', boxShadow: '0 24px 64px rgba(13,33,68,0.18)' },
      }}
    >
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
        {t('gmail.dialog.title')}
        <IconButton onClick={handleClose} size="small" sx={{ color: '#94A3B8' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Divider sx={{ borderColor: '#E2EAF4' }} />

      <DialogContent sx={{ px: 3, py: 3 }}>
        {sendError && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: '10px' }}>
            {sendError}
          </Alert>
        )}

        <TextField
          label={t('gmail.dialog.to')}
          placeholder={t('gmail.dialog.toPlaceholder')}
          value={form.to}
          onChange={(e) => set('to', e.target.value)}
          fullWidth
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        <TextField
          label={t('gmail.dialog.subject')}
          placeholder={t('gmail.dialog.subjectPlaceholder')}
          value={form.subject}
          onChange={(e) => set('subject', e.target.value)}
          fullWidth
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        <TextField
          label={t('gmail.dialog.body')}
          placeholder={t('gmail.dialog.bodyPlaceholder')}
          value={form.body}
          onChange={(e) => set('body', e.target.value)}
          fullWidth
          multiline
          minRows={5}
          size="small"
          sx={{ ...INPUT_SX, mb: 2 }}
        />

        {/* Lead link */}
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
            {t('gmail.dialog.linkLead')}
          </Typography>
          <Select
            value={form.leadId}
            onChange={(e) => set('leadId', e.target.value)}
            size="small"
            displayEmpty
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
            <MenuItem value="" sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#94A3B8' }}>
              {t('gmail.dialog.selectLead')}
            </MenuItem>
            {leads.map((lead) => (
              <MenuItem
                key={lead.id}
                value={lead.id}
                sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14 }}
              >
                {lead.first_name} {lead.last_name}
                {lead.company ? ` · ${lead.company}` : ''}
              </MenuItem>
            ))}
          </Select>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end' }}>
          <Button
            onClick={handleClose}
            disabled={sending}
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
            {t('gmail.dialog.cancel')}
          </Button>
          <Button
            onClick={handleSend}
            disabled={sending || !form.to.trim() || !form.subject.trim() || !form.body.trim()}
            variant="contained"
            startIcon={sending ? <CircularProgress size={14} color="inherit" /> : <SendIcon sx={{ fontSize: 16 }} />}
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
            {sending ? t('gmail.dialog.sending') : t('gmail.dialog.send')}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

/* ── Direction badge ── */
function DirectionBadge({ direction }: { direction: EmailDirection }) {
  const { t } = useTranslation();
  const isIn = direction === 'inbound';
  return (
    <Box
      sx={{
        display: 'inline-flex',
        px: 1.25,
        py: 0.3,
        borderRadius: '20px',
        bgcolor: isIn ? 'rgba(0,168,232,0.12)' : 'rgba(16,185,129,0.12)',
        color: isIn ? '#0090CC' : '#059669',
        fontFamily: 'Inter, sans-serif',
        fontSize: 11,
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      {t(`gmail.direction.${direction}`)}
    </Box>
  );
}

/* ── Skeleton rows ── */
function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 5 }).map((_, i) => (
        <TableRow key={i} sx={{ height: 56 }}>
          <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
            <Skeleton variant="rounded" width={72} height={22} sx={{ borderRadius: '20px' }} />
          </TableCell>
          <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
            <Skeleton variant="text" width={160} />
          </TableCell>
          <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
            <Skeleton variant="text" width="80%" />
          </TableCell>
          <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
            <Skeleton variant="text" width={80} />
          </TableCell>
          <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
            <Skeleton variant="rounded" width={64} height={20} sx={{ borderRadius: '20px' }} />
          </TableCell>
        </TableRow>
      ))}
    </>
  );
}

/* ── Thread dialog ── */
function ThreadDialog({
  threadId,
  onClose,
}: {
  threadId: string | null;
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const [detail, setDetail] = useState<EmailThreadDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!threadId) { setDetail(null); return; }
    setLoading(true);
    gmailApi.getThread(threadId)
      .then(setDetail)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [threadId]);

  const open = threadId !== null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { borderRadius: '20px', boxShadow: '0 24px 64px rgba(13,33,68,0.18)' } }}
    >
      <DialogTitle sx={{
        fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 16, color: '#0D2144',
        px: 3, pt: 3, pb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        {detail?.subject ?? '...'}
        <IconButton onClick={onClose} size="small" sx={{ color: '#94A3B8' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>
      <Divider sx={{ borderColor: '#E2EAF4' }} />
      <DialogContent sx={{ px: 3, py: 2, maxHeight: '70vh', overflowY: 'auto' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress sx={{ color: '#00A8E8' }} size={28} />
          </Box>
        ) : detail?.messages.map((msg, i) => (
          <Box key={msg.id} sx={{
            mb: 2, p: 2.5,
            bgcolor: msg.direction === 'inbound' ? '#F8FAFC' : 'rgba(0,168,232,0.04)',
            border: '1px solid #E8EFF7', borderRadius: '10px',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{
                  width: 28, height: 28, borderRadius: '50%',
                  bgcolor: msg.direction === 'inbound' ? 'rgba(0,168,232,0.15)' : 'rgba(16,185,129,0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'Inter', fontWeight: 700, fontSize: 11,
                  color: msg.direction === 'inbound' ? '#0090CC' : '#059669',
                  flexShrink: 0,
                }}>
                  {(msg.from_address[0] ?? '?').toUpperCase()}
                </Box>
                <Box>
                  <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 13, color: '#0D2144' }}>
                    {msg.from_address}
                  </Typography>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8' }}>
                    {t(`gmail.direction.${msg.direction}`)} · {new Date(msg.received_at).toLocaleString(undefined, { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                  </Typography>
                </Box>
              </Box>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#CBD5E8' }}>
                #{i + 1}
              </Typography>
            </Box>
            <Typography sx={{
              fontFamily: 'Inter', fontSize: 13, color: '#334155',
              lineHeight: 1.7, whiteSpace: 'pre-wrap',
              borderTop: '1px solid #E8EFF7', pt: 1.5, mt: 0.5,
            }}>
              {msg.body || '(пустое тело письма)'}
            </Typography>
          </Box>
        ))}
      </DialogContent>
    </Dialog>
  );
}

/* ── Threads view ── */
function ThreadsView({
  threads,
  loading,
  search,
  leads,
  onThreadClick,
}: {
  threads: EmailThreadSummary[];
  loading: boolean;
  search: string;
  leads: { id: string; first_name: string; last_name: string }[];
  onThreadClick: (threadId: string) => void;
}) {
  const { t } = useTranslation();

  const filtered = useMemo(() => {
    if (!search.trim()) return threads;
    const q = search.toLowerCase();
    return threads.filter(
      (th) =>
        th.subject.toLowerCase().includes(q) ||
        th.participants.some((p) => p.toLowerCase().includes(q)),
    );
  }, [threads, search]);

  if (loading) return (
    <Box sx={CARD}>
      <Table sx={{ tableLayout: 'fixed' }}>
        <TableBody>
          {Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i} sx={{ height: 60 }}>
              <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                <Skeleton variant="text" width="60%" />
                <Skeleton variant="text" width="40%" />
              </TableCell>
              <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF', width: 80 }}>
                <Skeleton variant="rounded" width={50} height={20} sx={{ borderRadius: '20px' }} />
              </TableCell>
              <TableCell sx={{ border: 'none', borderTop: '1px solid #F0F5FF', width: 90 }}>
                <Skeleton variant="text" width={70} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );

  if (filtered.length === 0) return (
    <Box sx={CARD}>
      <EmptyState
        icon="mail"
        title={t('gmail.threads.noThreads')}
        subtitle={t('gmail.threads.noThreadsSubtitle')}
      />
    </Box>
  );

  return (
    <Box sx={CARD}>
      <Table sx={{ tableLayout: 'fixed' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: '#F8FAFC' }}>
            <TableCell sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8', border: 'none', py: 1.5, pl: 2.5 }}>
              {t('gmail.table.subject')}
            </TableCell>
            <TableCell sx={{ width: 90, fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8', border: 'none', py: 1.5 }}>
              {t('gmail.table.from')}
            </TableCell>
            <TableCell sx={{ width: 80, fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8', border: 'none', py: 1.5 }}>
              Msgs
            </TableCell>
            <TableCell sx={{ width: 100, fontFamily: 'Inter', fontSize: 11, fontWeight: 500, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#94A3B8', border: 'none', py: 1.5, pr: 2.5 }}>
              {t('gmail.table.date')}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filtered.map((th) => {
            const lead = th.lead_id ? leads.find((l) => l.id === th.lead_id) : null;
            const date = new Date(th.last_message_at).toLocaleDateString(undefined, { day: '2-digit', month: 'short' });
            return (
              <TableRow
                key={th.thread_id}
                onClick={() => onThreadClick(th.thread_id)}
                sx={{
                  height: 60, cursor: 'pointer',
                  '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                  '&:hover': { bgcolor: '#F0F5FF' },
                }}
              >
                <TableCell sx={{ py: 1, pl: 2.5 }}>
                  <Typography noWrap sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: '#0D2144' }}>
                    {th.subject}
                  </Typography>
                  <Typography noWrap sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8', mt: 0.25 }}>
                    {th.participants.slice(0, 2).join(', ')}
                  </Typography>
                </TableCell>
                <TableCell sx={{ py: 1 }}>
                  {lead ? (
                    <Box sx={{ display: 'inline-flex', px: 1, py: 0.3, borderRadius: '20px', bgcolor: 'rgba(13,33,68,0.08)', color: '#0D2144', fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
                      {lead.first_name} {lead.last_name}
                    </Box>
                  ) : (
                    <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#CBD5E8' }}>—</Typography>
                  )}
                </TableCell>
                <TableCell sx={{ py: 1 }}>
                  <Box sx={{ display: 'inline-flex', px: 1.25, py: 0.3, borderRadius: '20px', bgcolor: 'rgba(0,168,232,0.1)', color: '#0090CC', fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
                    {t('gmail.threads.messages', { count: th.message_count })}
                  </Box>
                </TableCell>
                <TableCell sx={{ py: 1, pr: 2.5 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>{date}</Typography>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Box>
  );
}

/* ── Main page ── */
type AuthState = 'loading' | 'not_connected' | 'awaiting_auth' | 'connected';

export default function GmailPage() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const { leads, fetchLeads } = useLeadStore();

  const [authState, setAuthState] = useState<AuthState>('loading');
  const [emails, setEmails] = useState<EmailMessage[]>([]);
  const [threads, setThreads] = useState<EmailThreadSummary[]>([]);
  const [emailsLoading, setEmailsLoading] = useState(false);
  const [threadsLoading, setThreadsLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [composeOpen, setComposeOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'flat' | 'threads'>('flat');
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);

  useEffect(() => {
    checkStatus();
    fetchLeads();
  }, []);

  async function checkStatus() {
    setConnecting(true);
    try {
      const status = await gmailApi.getAuthStatus();
      if (status.authorized) {
        setAuthState('connected');
        loadEmails();
        loadThreads();
      } else {
        setAuthState('not_connected');
      }
    } catch {
      setAuthError(t('gmail.errors.status'));
      setAuthState('not_connected');
    } finally {
      setConnecting(false);
    }
  }

  async function handleConnect() {
    setConnecting(true);
    setAuthError(null);
    try {
      const { auth_url } = await gmailApi.getAuthUrl();
      window.open(auth_url, '_blank', 'noopener,noreferrer');
      setAuthState('awaiting_auth');
    } catch {
      setAuthError(t('gmail.errors.authUrl'));
    } finally {
      setConnecting(false);
    }
  }

  async function handleRefreshStatus() {
    setConnecting(true);
    setAuthError(null);
    try {
      const status = await gmailApi.getAuthStatus();
      if (status.authorized) {
        setAuthState('connected');
        loadEmails();
        loadThreads();
      } else {
        setAuthError(t('gmail.notConnected'));
      }
    } catch {
      setAuthError(t('gmail.errors.status'));
    } finally {
      setConnecting(false);
    }
  }

  async function loadEmails() {
    setEmailsLoading(true);
    setFetchError(null);
    try {
      setEmails(await gmailApi.listEmails(100));
    } catch {
      setFetchError(t('gmail.errors.fetch'));
    } finally {
      setEmailsLoading(false);
    }
  }

  async function loadThreads() {
    setThreadsLoading(true);
    try {
      setThreads(await gmailApi.listThreads());
    } catch {
      // ignore — threads are a secondary view
    } finally {
      setThreadsLoading(false);
    }
  }

  async function handleSync() {
    setSyncing(true);
    setFetchError(null);
    setSyncSuccess(false);
    try {
      await gmailApi.triggerSync('', 100);
      setSyncSuccess(true);
      setTimeout(() => setSyncSuccess(false), 4000);
      // Reload stored list after a brief delay to pick up new messages
      setTimeout(() => { loadEmails(); loadThreads(); }, 3000);
    } catch {
      setFetchError(t('gmail.errors.fetch'));
    } finally {
      setSyncing(false);
    }
  }

  function handleSent(msg: EmailMessage) {
    setEmails((prev) => [msg, ...prev]);
    // Reload threads to include the new outbound message
    loadThreads();
  }

  const filtered = useMemo(() => {
    if (!search.trim()) return emails;
    const q = search.toLowerCase();
    return emails.filter(
      (e) =>
        e.subject.toLowerCase().includes(q) ||
        e.from_address.toLowerCase().includes(q) ||
        e.to_addresses.some((a) => a.toLowerCase().includes(q)),
    );
  }, [emails, search]);

  /* ── Loading state ── */
  if (authState === 'loading') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
        <CircularProgress sx={{ color: '#00A8E8' }} />
      </Box>
    );
  }

  /* ── Not connected / awaiting auth ── */
  if (authState === 'not_connected' || authState === 'awaiting_auth') {
    return (
      <Box>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 24,
            fontWeight: 700,
            color: '#0D2144',
            mb: 3,
          }}
        >
          {t('gmail.title')}
        </Typography>
        <ConnectCard
          onConnect={handleConnect}
          connecting={connecting}
          awaitingAuth={authState === 'awaiting_auth'}
          onRefreshStatus={handleRefreshStatus}
          error={authError}
        />
      </Box>
    );
  }

  /* ── Connected ── */
  return (
    <Box>
      {/* ── Header ── */}
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
            {t('gmail.title')}
          </Typography>
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 0.5,
              px: 1.25,
              py: 0.4,
              borderRadius: '20px',
              bgcolor: 'rgba(16,185,129,0.12)',
              color: '#059669',
              fontFamily: 'Inter, sans-serif',
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: '#10B981',
              }}
            />
            {t('gmail.connected')}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
          {/* View toggle */}
          <Box sx={{ display: 'flex', border: '1px solid #E2EAF4', borderRadius: '10px', overflow: 'hidden' }}>
            <Button
              onClick={() => setViewMode('flat')}
              sx={{
                fontFamily: 'Inter', fontWeight: 600, fontSize: 13,
                color: viewMode === 'flat' ? '#fff' : '#64748B',
                bgcolor: viewMode === 'flat' ? '#00A8E8' : 'transparent',
                borderRadius: 0, px: 2, py: 0.75, textTransform: 'none',
                '&:hover': { bgcolor: viewMode === 'flat' ? '#00A8E8' : '#F0F5FF' },
              }}
            >
              <InboxIcon sx={{ fontSize: 15, mr: 0.75 }} />
              {t('gmail.viewFlat')}
            </Button>
            <Button
              onClick={() => setViewMode('threads')}
              sx={{
                fontFamily: 'Inter', fontWeight: 600, fontSize: 13,
                color: viewMode === 'threads' ? '#fff' : '#64748B',
                bgcolor: viewMode === 'threads' ? '#00A8E8' : 'transparent',
                borderRadius: 0, px: 2, py: 0.75, textTransform: 'none',
                borderLeft: '1px solid #E2EAF4',
                '&:hover': { bgcolor: viewMode === 'threads' ? '#00A8E8' : '#F0F5FF' },
              }}
            >
              <ChatBubbleOutlineIcon sx={{ fontSize: 15, mr: 0.75 }} />
              {t('gmail.viewThreads')}
            </Button>
          </Box>

          <Button
            variant="outlined"
            startIcon={syncing ? <CircularProgress size={14} sx={{ color: '#00A8E8' }} /> : <SyncIcon />}
            onClick={handleSync}
            disabled={syncing}
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 14,
              color: '#00A8E8',
              borderColor: '#00A8E8',
              borderRadius: '10px',
              px: 2,
              textTransform: 'none',
              '&:hover': { bgcolor: '#E8F4FF', borderColor: '#0090CC' },
            }}
          >
            {syncing ? t('gmail.syncing') : t('gmail.sync')}
          </Button>
          <Button
            variant="contained"
            startIcon={<CreateIcon />}
            onClick={() => setComposeOpen(true)}
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
            {t('gmail.compose')}
          </Button>
        </Box>
      </Box>

      {fetchError && (
        <Alert severity="error" sx={{ mb: 2.5, borderRadius: '12px' }}>
          {fetchError}
        </Alert>
      )}

      <Collapse in={syncSuccess}>
        <Alert severity="success" sx={{ mb: 2.5, borderRadius: '12px' }}>
          {t('gmail.syncQueued')}
        </Alert>
      </Collapse>

      {/* ── Search ── */}
      <Box sx={{ mb: 2.5 }}>
        <TextField
          size="small"
          placeholder={t('gmail.search')}
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
            width: 320,
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
      </Box>

      {/* ── Email table / Threads view ── */}
      {viewMode === 'threads' ? (
        <ThreadsView
          threads={threads}
          loading={threadsLoading}
          search={search}
          leads={leads}
          onThreadClick={setActiveThreadId}
        />
      ) : (
      <Box sx={CARD}>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {/* Direction */}
              <TableCell
                sx={{
                  width: 100,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  pl: 2.5,
                }}
              />
              {/* From */}
              <TableCell
                sx={{
                  width: '22%',
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
                {t('gmail.table.from')}
              </TableCell>
              {/* Subject */}
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
                {t('gmail.table.subject')}
              </TableCell>
              {/* Date */}
              <TableCell
                sx={{
                  width: '12%',
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
                {t('gmail.table.date')}
              </TableCell>
              {/* Lead */}
              <TableCell
                sx={{
                  width: '14%',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  pr: 2.5,
                }}
              >
                {t('gmail.table.lead')}
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {emailsLoading ? (
              <SkeletonRows />
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} sx={{ border: 'none' }}>
                  <EmptyState
                    icon="mail"
                    title={t('gmail.noEmails')}
                    subtitle={t('gmail.noEmailsSubtitle')}
                  />
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((email) => {
                const lead = email.lead_id
                  ? leads.find((l) => l.id === email.lead_id)
                  : null;
                const date = new Date(email.received_at).toLocaleDateString(undefined, {
                  day: '2-digit',
                  month: 'short',
                });
                const counterparty =
                  email.direction === 'inbound'
                    ? email.from_address
                    : email.to_addresses[0] ?? '—';

                return (
                  <TableRow
                    key={email.id}
                    sx={{
                      height: 56,
                      '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                      '&:hover': { bgcolor: '#F0F5FF' },
                    }}
                  >
                    {/* Direction badge */}
                    <TableCell sx={{ py: 1, pl: 2.5 }}>
                      <DirectionBadge direction={email.direction} />
                    </TableCell>

                    {/* From / To */}
                    <TableCell sx={{ py: 1 }}>
                      <Tooltip title={counterparty}>
                        <Typography
                          noWrap
                          sx={{
                            fontFamily: 'Inter, sans-serif',
                            fontSize: 13,
                            fontWeight: 500,
                            color: '#0D2144',
                            maxWidth: 180,
                          }}
                        >
                          {counterparty}
                        </Typography>
                      </Tooltip>
                    </TableCell>

                    {/* Subject */}
                    <TableCell sx={{ py: 1 }}>
                      <Tooltip title={email.subject}>
                        <Typography
                          noWrap
                          sx={{
                            fontFamily: 'Inter, sans-serif',
                            fontSize: 13,
                            color: '#4B6080',
                          }}
                        >
                          {email.subject}
                        </Typography>
                      </Tooltip>
                    </TableCell>

                    {/* Date */}
                    <TableCell sx={{ py: 1 }}>
                      <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>
                        {date}
                      </Typography>
                    </TableCell>

                    {/* Lead */}
                    <TableCell sx={{ py: 1, pr: 2.5 }}>
                      {lead ? (
                        <Box
                          sx={{
                            display: 'inline-flex',
                            px: 1,
                            py: 0.3,
                            borderRadius: '20px',
                            bgcolor: 'rgba(13,33,68,0.08)',
                            color: '#0D2144',
                            fontFamily: 'Inter',
                            fontSize: 11,
                            fontWeight: 600,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            maxWidth: 120,
                          }}
                        >
                          {lead.first_name} {lead.last_name}
                        </Box>
                      ) : (
                        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#CBD5E8' }}>
                          —
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Box>
      )}

      {/* ── Thread dialog ── */}
      <ThreadDialog threadId={activeThreadId} onClose={() => setActiveThreadId(null)} />

      {/* ── Compose dialog ── */}
      <ComposeDialog
        open={composeOpen}
        onClose={() => setComposeOpen(false)}
        onSent={handleSent}
        userId={user?.id ?? ''}
      />
    </Box>
  );
}
