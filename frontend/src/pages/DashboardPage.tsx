import AccountTreeIcon from '@mui/icons-material/AccountTree';
import PeopleIcon from '@mui/icons-material/People';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import WorkIcon from '@mui/icons-material/Work';
import { Alert, Box, Grid, IconButton, Skeleton, Tooltip, Typography } from '@mui/material';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import AIInsightsPanel from '../components/dashboard/AIInsightsPanel';
import DealsStatusChart from '../components/dashboard/DealsStatusChart';
import LeadsStatusChart from '../components/dashboard/LeadsStatusChart';
import StatCard from '../components/dashboard/StatCard';
import { useAuthStore } from '../store/useAuthStore';
import { useDashboardStore } from '../store/useDashboardStore';

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

/* ── Pipeline health: deals breakdown with progress bars ── */
function PipelineHealthCard({
  data,
  loading,
}: {
  data: { open: number; won: number; lost: number } | null;
  loading: boolean;
}) {
  const { t } = useTranslation();
  const total = data ? data.open + data.won + data.lost : 0;

  const rows = data
    ? [
        { label: t('dashboard.charts.open'), value: data.open, color: '#00A8E8' },
        { label: t('dashboard.charts.won'), value: data.won, color: '#10B981' },
        { label: t('dashboard.charts.lost'), value: data.lost, color: '#EF4444' },
      ]
    : [];

  return (
    <Box
      sx={{
        height: '100%',
        bgcolor: 'background.paper',
        border: '1px solid', borderColor: 'divider',
        borderRadius: '16px',
        boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
        p: 2.5,
      }}
    >
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          fontSize: 15,
          color: 'text.primary',
          mb: 2,
        }}
      >
        {t('dashboard.pipelineHealth')}
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rounded" height={40} />
          <Skeleton variant="rounded" height={40} />
          <Skeleton variant="rounded" height={40} />
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          {rows.map((row) => {
            const pct = total > 0 ? Math.round((row.value / total) * 100) : 0;
            return (
              <Box key={row.label}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 0.75,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: row.color,
                        flexShrink: 0,
                      }}
                    />
                    <Typography
                      sx={{
                        fontFamily: 'Inter, sans-serif',
                        fontSize: 13,
                        fontWeight: 500,
                        color: 'text.secondary',
                      }}
                    >
                      {row.label}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Typography
                      sx={{
                        fontFamily: 'Inter, sans-serif',
                        fontSize: 13,
                        fontWeight: 700,
                        color: 'text.primary',
                      }}
                    >
                      {row.value}
                    </Typography>
                    <Typography sx={{ fontSize: 11, color: '#94A3B8' }}>{pct}%</Typography>
                  </Box>
                </Box>
                <Box
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    bgcolor: 'action.hover',
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      height: '100%',
                      width: `${pct}%`,
                      bgcolor: row.color,
                      borderRadius: 3,
                      transition: 'width 0.6s ease',
                    }}
                  />
                </Box>
              </Box>
            );
          })}
        </Box>
      )}
    </Box>
  );
}

/* ── Main page ── */
export default function DashboardPage() {
  const { t } = useTranslation();
  const { data, loading, error, fetchDashboard } = useDashboardStore();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return (
    <Box>
      {/* Page header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          mb: 3,
        }}
      >
        <Box>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 24,
              fontWeight: 700,
              color: 'text.primary',
              lineHeight: 1.2,
            }}
          >
            {t('dashboard.title')}
          </Typography>
          <Typography sx={{ fontSize: 14, color: 'text.secondary', mt: 0.5 }}>
            {user?.first_name ? `${user.first_name} · ` : ''}
            {t('dashboard.greeting')}
          </Typography>
        </Box>
        <Tooltip title={t('dashboard.refresh')}>
          <IconButton
            onClick={fetchDashboard}
            disabled={loading}
            size="small"
            sx={{
              border: '1px solid', borderColor: 'divider',
              borderRadius: '10px',
              color: 'text.secondary',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      {/* ── Row 1: KPI cards ── */}
      <Grid container spacing={2.5} sx={{ mb: 2.5 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('dashboard.kpi.pipelineValue')}
            value={data ? formatCurrency(data.pipeline_value) : '—'}
            icon={<AccountTreeIcon fontSize="small" />}
            accentColor="#00A8E8"
            subtext={t('dashboard.kpi.openDeals', { count: data?.open_deals ?? 0 })}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('dashboard.kpi.activeDeals')}
            value={data?.open_deals ?? '—'}
            icon={<WorkIcon fontSize="small" />}
            accentColor="#0D2144"
            subtext={t('dashboard.kpi.totalDeals', { count: data?.total_deals ?? 0 })}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('dashboard.kpi.leadConversion')}
            value={data ? `${data.conversion_rate}%` : '—'}
            icon={<PeopleIcon fontSize="small" />}
            accentColor="#10B981"
            subtext={t('dashboard.kpi.totalLeads', { count: data?.total_leads ?? 0 })}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {(() => {
            const won = data?.deals_by_status?.won ?? 0;
            const lost = data?.deals_by_status?.lost ?? 0;
            const decided = won + lost;
            const winRate = decided > 0 ? Math.round(won / decided * 100) : null;
            return (
              <StatCard
                label={t('dashboard.kpi.winRate')}
                value={winRate !== null ? `${winRate}%` : '—'}
                icon={<ShowChartIcon fontSize="small" />}
                accentColor="#F59E0B"
                subtext={t('dashboard.kpi.wonDeals', { won, lost })}
                loading={loading}
              />
            );
          })()}
        </Grid>
      </Grid>

      {/* ── Row 2: Deals chart + AI Insights ── */}
      <Grid container spacing={2.5} sx={{ mb: 2.5 }}>
        <Grid item xs={12} md={8}>
          <DealsStatusChart data={data?.deals_by_status ?? null} loading={loading} />
        </Grid>
        <Grid item xs={12} md={4}>
          <AIInsightsPanel data={data} loading={loading} />
        </Grid>
      </Grid>

      {/* ── Row 3: Leads chart + Pipeline health ── */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <LeadsStatusChart data={data?.leads_by_status ?? null} loading={loading} />
        </Grid>
        <Grid item xs={12} md={6}>
          <PipelineHealthCard data={data?.deals_by_status ?? null} loading={loading} />
        </Grid>
      </Grid>
    </Box>
  );
}
