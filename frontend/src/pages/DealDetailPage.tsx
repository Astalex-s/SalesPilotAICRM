import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Skeleton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { dealsApi } from '../api/deals';
import { type Activity } from '../types/activity';
import { type Deal } from '../types/deal';

function fmt(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

const STATUS_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  open: { bg: 'rgba(0,168,232,0.12)', color: '#0090CC', label: 'Open' },
  won:  { bg: 'rgba(16,185,129,0.12)', color: '#059669', label: 'Won' },
  lost: { bg: 'rgba(239,68,68,0.12)', color: '#DC2626', label: 'Lost' },
};

export default function DealDetailPage() {
  const { t } = useTranslation();
  const { dealId } = useParams<{ dealId: string }>();
  const navigate = useNavigate();

  const [deal, setDeal] = useState<Deal | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [closing, setClosing] = useState(false);

  useEffect(() => {
    if (!dealId) return;
    setLoading(true);
    Promise.all([
      dealsApi.getById(dealId),
      dealsApi.getActivities(dealId),
    ])
      .then(([d, a]) => { setDeal(d); setActivities(a); })
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [dealId]);

  const handleClose = async (outcome: 'won' | 'lost') => {
    if (!dealId) return;
    setClosing(true);
    try {
      const updated = await dealsApi.close(dealId, outcome);
      setDeal(updated);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setClosing(false);
    }
  };

  const handleDelete = async () => {
    if (!dealId || !window.confirm(t('dealDetail.deleteConfirm'))) return;
    await dealsApi.delete(dealId);
    navigate('/deals');
  };

  if (error) {
    return <Alert severity="error" sx={{ borderRadius: '12px' }}>{error}</Alert>;
  }

  const s = deal ? STATUS_STYLE[deal.status] ?? STATUS_STYLE.open : STATUS_STYLE.open;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Tooltip title={t('dealDetail.back')}>
          <IconButton
            onClick={() => navigate('/deals')}
            size="small"
            sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '10px', color: 'text.secondary' }}
          >
            <ArrowBackIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        {loading ? (
          <Skeleton variant="text" width={250} height={32} />
        ) : deal ? (
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: 'text.primary' }}>
            {deal.title}
          </Typography>
        ) : null}
      </Box>

      <Grid container spacing={2.5} alignItems="flex-start">
        {/* Left — Deal Info */}
        <Grid item xs={12} md={4}>
          {loading ? (
            <Skeleton variant="rounded" height={350} sx={{ borderRadius: '16px' }} />
          ) : deal ? (
            <Card elevation={0} sx={{ bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: '16px', boxShadow: '0 4px 24px rgba(13,33,68,0.07)' }}>
              <Box sx={{ p: 2.5 }}>
                {/* Status */}
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  <Chip label={s.label} sx={{ bgcolor: s.bg, color: s.color, fontWeight: 600, fontSize: 12 }} />
                </Box>

                {/* Value */}
                <Typography sx={{ fontFamily: 'Inter', fontSize: 32, fontWeight: 700, color: '#00A8E8', textAlign: 'center', mb: 2 }}>
                  {fmt(Number(deal.value_amount))}
                </Typography>

                <Divider sx={{ borderColor: 'divider', my: 2 }} />

                {/* Details */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {deal.company && (
                    <InfoRow label={t('dealDetail.company')} value={deal.company} />
                  )}
                  {deal.contact_name && (
                    <InfoRow label={t('dealDetail.contact')} value={deal.contact_name} />
                  )}
                  {deal.expected_close_date && (
                    <InfoRow
                      label={t('dealDetail.closeDate')}
                      value={new Date(deal.expected_close_date).toLocaleDateString()}
                    />
                  )}
                  <InfoRow label={t('dealDetail.created')} value={new Date(deal.created_at).toLocaleDateString()} />
                </Box>

                {/* Close buttons */}
                {deal.status === 'open' && (
                  <>
                    <Divider sx={{ borderColor: 'divider', my: 2 }} />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        fullWidth size="small" variant="contained"
                        onClick={() => handleClose('won')}
                        disabled={closing}
                        sx={{ bgcolor: '#10B981', '&:hover': { bgcolor: '#059669' }, textTransform: 'none', fontFamily: 'Inter', fontWeight: 600 }}
                      >
                        {closing ? <CircularProgress size={16} /> : t('dealDetail.won')}
                      </Button>
                      <Button
                        fullWidth size="small" variant="contained"
                        onClick={() => handleClose('lost')}
                        disabled={closing}
                        sx={{ bgcolor: '#EF4444', '&:hover': { bgcolor: '#DC2626' }, textTransform: 'none', fontFamily: 'Inter', fontWeight: 600 }}
                      >
                        {closing ? <CircularProgress size={16} /> : t('dealDetail.lost')}
                      </Button>
                    </Box>
                  </>
                )}

                {/* Delete */}
                <Divider sx={{ borderColor: 'divider', my: 2 }} />
                <Box
                  onClick={handleDelete}
                  sx={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.75,
                    py: 1, borderRadius: '8px', cursor: 'pointer',
                    color: '#EF4444', fontSize: 13, fontFamily: 'Inter', fontWeight: 500,
                    '&:hover': { bgcolor: 'rgba(239,68,68,0.08)' },
                    transition: 'background 0.15s',
                  }}
                >
                  <DeleteOutlineIcon sx={{ fontSize: 16 }} />
                  {t('dealDetail.delete')}
                </Box>
              </Box>
            </Card>
          ) : null}
        </Grid>

        {/* Right — Activities */}
        <Grid item xs={12} md={8}>
          <Card elevation={0} sx={{ bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: '16px', boxShadow: '0 4px 24px rgba(13,33,68,0.07)' }}>
            <Box sx={{ p: 2.5 }}>
              <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 15, color: 'text.primary', mb: 2 }}>
                {t('dealDetail.activities')}
              </Typography>
              {loading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={60} sx={{ borderRadius: '10px' }} />)}
                </Box>
              ) : activities.length === 0 ? (
                <Typography sx={{ fontSize: 13, color: '#94A3B8', textAlign: 'center', py: 4 }}>
                  {t('dealDetail.noActivities')}
                </Typography>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {activities.map((a) => (
                    <Box
                      key={a.id}
                      sx={{ p: 1.5, borderRadius: '10px', bgcolor: 'background.default', border: '1px solid', borderColor: 'divider' }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography sx={{ fontSize: 12, fontWeight: 600, color: '#00A8E8', fontFamily: 'Inter', textTransform: 'uppercase' }}>
                          {a.activity_type}
                        </Typography>
                        <Typography sx={{ fontSize: 11, color: '#94A3B8', fontFamily: 'Inter' }}>
                          {new Date(a.occurred_at).toLocaleString()}
                        </Typography>
                      </Box>
                      <Typography sx={{ fontSize: 13, color: 'text.primary', fontFamily: 'Inter' }}>
                        {a.body}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
      <Typography sx={{ fontSize: 12, color: '#94A3B8', fontFamily: 'Inter' }}>{label}</Typography>
      <Typography sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary', fontFamily: 'Inter' }}>{value}</Typography>
    </Box>
  );
}
