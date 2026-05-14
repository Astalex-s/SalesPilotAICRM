import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import RefreshIcon from '@mui/icons-material/Refresh';
import SendIcon from '@mui/icons-material/Send';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Grid,
  IconButton,
  Skeleton,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { telegramApi } from '../api/telegram';
import type { TelegramStatus } from '../types/telegram';

/* ── Design tokens ── */
const CARD = {
  bgcolor: 'background.paper',
  border: '1px solid', borderColor: 'divider',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
  p: 2.5,
};

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

/* ── Status row ── */
function StatusRow({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string | number;
  highlight?: 'ok' | 'warn' | 'neutral';
}) {
  const color =
    highlight === 'ok' ? '#059669' :
    highlight === 'warn' ? '#DC2626' :
    '#4B6080';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        py: 1.25,
        borderBottom: '1px solid #F0F5FF',
        '&:last-child': { borderBottom: 'none' },
      }}
    >
      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#94A3B8' }}>
        {label}
      </Typography>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 13,
          fontWeight: 600,
          color,
          maxWidth: '60%',
          textAlign: 'right',
          wordBreak: 'break-all',
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}

/* ── Not configured card ── */
function NotConfiguredCard() {
  const { t } = useTranslation();
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 320,
      }}
    >
      <Box sx={{ ...CARD, maxWidth: 520, width: '100%', textAlign: 'center' }}>
        <Box
          sx={{
            width: 56,
            height: 56,
            borderRadius: '14px',
            bgcolor: 'rgba(245,158,11,0.1)',
            color: '#F59E0B',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2,
          }}
        >
          <NotificationsActiveIcon sx={{ fontSize: 28 }} />
        </Box>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 18,
            color: 'text.primary',
            mb: 1,
          }}
        >
          {t('telegram.notConfiguredCard.title')}
        </Typography>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 14,
            color: '#94A3B8',
            lineHeight: 1.6,
            mb: 2,
          }}
        >
          {t('telegram.notConfiguredCard.desc')}
        </Typography>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 1,
            p: '10px 14px',
            borderRadius: '10px',
            bgcolor: 'background.default',
            border: '1px solid', borderColor: 'divider',
            textAlign: 'left',
          }}
        >
          <InfoOutlinedIcon sx={{ fontSize: 16, color: '#94A3B8', mt: '1px', flexShrink: 0 }} />
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'text.secondary', lineHeight: 1.5 }}>
            {t('telegram.notConfiguredCard.hint')}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

/* ── Status card ── */
function StatusCard({
  status,
  loading,
  onRefresh,
}: {
  status: TelegramStatus | null;
  loading: boolean;
  onRefresh: () => void;
}) {
  const { t } = useTranslation();

  return (
    <Box sx={CARD}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography
          sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: 'text.primary' }}
        >
          {t('telegram.statusCard.title')}
        </Typography>
        <Tooltip title={t('telegram.statusCard.refresh')}>
          <IconButton
            size="small"
            onClick={onRefresh}
            disabled={loading}
            sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '8px', color: 'text.secondary', '&:hover': { bgcolor: 'action.hover' } }}
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {Array.from({ length: 3 }).map((_, i) => (
            <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', py: 1.25, borderBottom: '1px solid #F0F5FF' }}>
              <Skeleton variant="text" width={100} />
              <Skeleton variant="text" width={120} />
            </Box>
          ))}
        </Box>
      ) : status ? (
        <>
          <StatusRow
            label={t('telegram.statusCard.token')}
            value={status.configured ? t('telegram.statusCard.tokenSet') : t('telegram.statusCard.tokenMissing')}
            highlight={status.configured ? 'ok' : 'warn'}
          />
          <StatusRow
            label={t('telegram.statusCard.webhook')}
            value={status.webhook_url || t('telegram.statusCard.webhookNone')}
            highlight={status.webhook_url ? 'ok' : 'neutral'}
          />
          <StatusRow
            label={t('telegram.statusCard.pending')}
            value={status.webhook_pending_updates}
            highlight="neutral"
          />
        </>
      ) : null}
    </Box>
  );
}

/* ── Capabilities card ── */
function CapabilitiesCard() {
  const { t } = useTranslation();
  const items = t('telegram.capabilitiesCard.items', { returnObjects: true }) as string[];

  return (
    <Box sx={CARD}>
      <Typography
        sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: 'text.primary', mb: 2 }}
      >
        {t('telegram.capabilitiesCard.title')}
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.25 }}>
        {items.map((item, i) => (
          <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.25 }}>
            <CheckCircleIcon sx={{ fontSize: 16, color: '#10B981', mt: '2px', flexShrink: 0 }} />
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'text.secondary', lineHeight: 1.5 }}>
              {item}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}

/* ── Webhook form ── */
function WebhookCard({ onSuccess }: { onSuccess: () => void }) {
  const { t } = useTranslation();
  const [url, setUrl] = useState('');
  const [secret, setSecret] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  async function handleSubmit() {
    if (!url.trim()) return;
    setSubmitting(true);
    setError(null);
    setSuccessMsg(null);
    try {
      await telegramApi.setWebhook(url.trim(), secret.trim() || undefined);
      setSuccessMsg(t('telegram.webhookCard.success'));
      onSuccess();
    } catch {
      setError(t('telegram.errors.webhook'));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Box sx={CARD}>
      <Typography
        sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: 'text.primary', mb: 0.75 }}
      >
        {t('telegram.webhookCard.title')}
      </Typography>
      <Typography
        sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#94A3B8', lineHeight: 1.5, mb: 2.5 }}
      >
        {t('telegram.webhookCard.desc')}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }}>
          {error}
        </Alert>
      )}
      {successMsg && (
        <Alert severity="success" sx={{ mb: 2, borderRadius: '10px' }}>
          {successMsg}
        </Alert>
      )}

      <TextField
        label={t('telegram.webhookCard.urlLabel')}
        placeholder={t('telegram.webhookCard.urlPlaceholder')}
        value={url}
        onChange={(e) => { setUrl(e.target.value); setError(null); }}
        fullWidth
        size="small"
        sx={{ ...INPUT_SX, mb: 2 }}
      />

      <TextField
        label={t('telegram.webhookCard.secretLabel')}
        placeholder={t('telegram.webhookCard.secretPlaceholder')}
        value={secret}
        onChange={(e) => setSecret(e.target.value)}
        fullWidth
        size="small"
        sx={{ ...INPUT_SX, mb: 2.5 }}
      />

      <Button
        variant="contained"
        startIcon={
          submitting
            ? <CircularProgress size={14} color="inherit" />
            : <SendIcon sx={{ fontSize: 16 }} />
        }
        onClick={handleSubmit}
        disabled={submitting || !url.trim()}
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
          '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
        }}
      >
        {submitting ? t('telegram.webhookCard.submitting') : t('telegram.webhookCard.submit')}
      </Button>
    </Box>
  );
}

/* ── Main page ── */
export default function TelegramPage() {
  const { t } = useTranslation();
  const [status, setStatus] = useState<TelegramStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadStatus() {
    setLoading(true);
    setError(null);
    try {
      const data = await telegramApi.getStatus();
      setStatus(data);
    } catch {
      setError(t('telegram.errors.status'));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadStatus(); }, []);

  return (
    <Box>
      {/* ── Header ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 24,
            fontWeight: 700,
            color: 'text.primary',
          }}
        >
          {t('telegram.title')}
        </Typography>

        {!loading && status && (
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 0.5,
              px: 1.25,
              py: 0.4,
              borderRadius: '20px',
              bgcolor: status.configured
                ? 'rgba(16,185,129,0.12)'
                : 'rgba(245,158,11,0.12)',
              color: status.configured ? '#059669' : '#D97706',
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
                bgcolor: status.configured ? '#10B981' : '#F59E0B',
              }}
            />
            {status.configured ? t('telegram.configured') : t('telegram.notConfigured')}
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      {/* Not configured state */}
      {!loading && status && !status.configured ? (
        <NotConfiguredCard />
      ) : (
        <Grid container spacing={2.5}>
          {/* Left column */}
          <Grid item xs={12} md={5}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              <StatusCard status={status} loading={loading} onRefresh={loadStatus} />
              <CapabilitiesCard />
            </Box>
          </Grid>

          {/* Right column */}
          <Grid item xs={12} md={7}>
            <WebhookCard onSuccess={loadStatus} />
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
