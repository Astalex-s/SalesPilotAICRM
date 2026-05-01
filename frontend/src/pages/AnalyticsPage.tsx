import RefreshIcon from '@mui/icons-material/Refresh';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import {
  Alert,
  Box,
  Grid,
  IconButton,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip as RTooltip,
  XAxis,
  YAxis,
} from 'recharts';
import StatCard from '../components/dashboard/StatCard';
import { analyticsApi } from '../api/analytics';
import { type AnalyticsOverview, type RevenueForecast } from '../types/analytics';

/* ── Design tokens ── */
const CARD = {
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

const FUNNEL_COLORS: Record<string, string> = {
  new:         '#00A8E8',
  contacted:   '#F59E0B',
  qualified:   '#10B981',
  unqualified: '#EF4444',
  converted:   '#0D2144',
};

/* ── Currency formatter ── */
function fmt(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

/* ── Conversion Funnel Chart ── */
function ConversionFunnelCard({
  overview,
  loading,
}: {
  overview: AnalyticsOverview | null;
  loading: boolean;
}) {
  const { t } = useTranslation();

  const chartData = overview?.conversion_funnel.map((step) => ({
    name: t(`analytics.funnel.statuses.${step.status}`, step.status),
    count: step.count,
    pct: step.percentage,
    color: FUNNEL_COLORS[step.status] ?? '#94A3B8',
  })) ?? [];

  return (
    <Box sx={{ ...CARD, p: 2.5, height: '100%' }}>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          fontSize: 15,
          color: '#0D2144',
          mb: 2,
        }}
      >
        {t('analytics.funnel.title')}
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="rounded" height={36} sx={{ borderRadius: '8px' }} />
          ))}
        </Box>
      ) : chartData.length === 0 ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200 }}>
          <Typography sx={{ fontSize: 13, color: '#94A3B8' }}>
            {t('analytics.pipelineStats.noData')}
          </Typography>
        </Box>
      ) : (
        <Box sx={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 0, right: 48, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2EAF4" />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Inter, sans-serif' }}
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={88}
                tick={{ fontSize: 12, fill: '#4B6080', fontFamily: 'Inter, sans-serif' }}
                axisLine={false}
                tickLine={false}
              />
              <RTooltip
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                formatter={(value: number, _name: string, props: any) => [
                  `${value} (${(props?.payload?.pct as number | undefined)?.toFixed(1) ?? 0}%)`,
                  t('analytics.funnel.leads'),
                ]}
                contentStyle={{
                  background: '#0D2144',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#FFFFFF',
                  fontSize: 12,
                  fontFamily: 'Inter, sans-serif',
                }}
                itemStyle={{ color: '#FFFFFF' }}
                labelStyle={{ color: '#94A3B8', marginBottom: 2 }}
                cursor={{ fill: 'rgba(0,168,232,0.06)' }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={28}>
                {chartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Box>
  );
}

/* ── Revenue Forecast Card ── */
function RevenueForecastCard({
  forecast,
  loading,
}: {
  forecast: RevenueForecast | null;
  loading: boolean;
}) {
  const { t } = useTranslation();

  const metrics = forecast
    ? [
        { label: t('analytics.forecast.closed'),   value: fmt(forecast.closed_revenue),   color: '#10B981' },
        { label: t('analytics.forecast.pipeline'),  value: fmt(forecast.pipeline_value),   color: '#00A8E8' },
        { label: t('analytics.forecast.weighted'),  value: fmt(forecast.weighted_forecast), color: '#F59E0B' },
      ]
    : [];

  const barData = forecast?.by_pipeline.map((p) => ({
    name: p.pipeline_name,
    closed: p.closed_revenue,
    forecast: p.weighted_forecast,
  })) ?? [];

  return (
    <Box sx={{ ...CARD, p: 2.5, height: '100%' }}>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          fontSize: 15,
          color: '#0D2144',
          mb: 2,
        }}
      >
        {t('analytics.forecast.title')}
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rounded" height={60} sx={{ borderRadius: '10px' }} />
          <Skeleton variant="rounded" height={60} sx={{ borderRadius: '10px' }} />
          <Skeleton variant="rounded" height={60} sx={{ borderRadius: '10px' }} />
        </Box>
      ) : (
        <>
          {/* Metric rows */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mb: 2.5 }}>
            {metrics.map((m) => (
              <Box
                key={m.label}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  p: '10px 14px',
                  borderRadius: '10px',
                  bgcolor: '#F7F9FC',
                  border: '1px solid #E2EAF4',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: m.color,
                      flexShrink: 0,
                    }}
                  />
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 13,
                      fontWeight: 500,
                      color: '#4B6080',
                    }}
                  >
                    {m.label}
                  </Typography>
                </Box>
                <Typography
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 16,
                    fontWeight: 700,
                    color: '#0D2144',
                  }}
                >
                  {m.value}
                </Typography>
              </Box>
            ))}
          </Box>

          {/* Per-pipeline mini chart (if multiple pipelines) */}
          {barData.length > 0 && (
            <Box sx={{ height: 120 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 0, right: 0, left: -16, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2EAF4" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10, fill: '#94A3B8', fontFamily: 'Inter, sans-serif' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis hide />
                  <RTooltip
                    formatter={(value: number, name: string) => [
                      fmt(value),
                      name === 'closed' ? t('analytics.forecast.closed') : t('analytics.forecast.weighted'),
                    ]}
                    contentStyle={{
                      background: '#0D2144',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#FFFFFF',
                      fontSize: 11,
                      fontFamily: 'Inter, sans-serif',
                    }}
                    itemStyle={{ color: '#FFFFFF' }}
                    cursor={{ fill: 'rgba(0,168,232,0.06)' }}
                  />
                  <Bar dataKey="closed" fill="#10B981" radius={[4, 4, 0, 0]} maxBarSize={24} />
                  <Bar dataKey="forecast" fill="#F59E0B" radius={[4, 4, 0, 0]} maxBarSize={24} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

/* ── Pipeline Stats Table ── */
function PipelineStatsTable({
  overview,
  loading,
}: {
  overview: AnalyticsOverview | null;
  loading: boolean;
}) {
  const { t } = useTranslation();

  const headers = [
    t('analytics.pipelineStats.pipeline'),
    t('analytics.pipelineStats.total'),
    t('analytics.pipelineStats.open'),
    t('analytics.pipelineStats.won'),
    t('analytics.pipelineStats.lost'),
    t('analytics.pipelineStats.value'),
    t('analytics.pipelineStats.revenue'),
    t('analytics.pipelineStats.winRate'),
    t('analytics.pipelineStats.avgDeal'),
  ];

  return (
    <Box sx={CARD}>
      <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 15,
            color: '#0D2144',
          }}
        >
          {t('analytics.pipelineStats.title')}
        </Typography>
      </Box>

      <Table sx={{ tableLayout: 'fixed' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: '#F8FAFC' }}>
            {headers.map((h, i) => (
              <TableCell
                key={i}
                align={i === 0 ? 'left' : 'right'}
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 500,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                  color: '#94A3B8',
                  border: 'none',
                  py: 1.5,
                  px: i === 0 ? 2.5 : 2,
                  width: i === 0 ? '20%' : '10%',
                }}
              >
                {h}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>

        <TableBody>
          {loading ? (
            Array.from({ length: 2 }).map((_, i) => (
              <TableRow key={i} sx={{ height: 52 }}>
                {Array.from({ length: 9 }).map((__, j) => (
                  <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                    <Skeleton variant="text" width="80%" />
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : !overview || overview.pipeline_stats.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={9}
                align="center"
                sx={{
                  py: 6,
                  border: 'none',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  color: '#94A3B8',
                }}
              >
                {t('analytics.pipelineStats.noData')}
              </TableCell>
            </TableRow>
          ) : (
            overview.pipeline_stats.map((p) => (
              <TableRow
                key={p.pipeline_id}
                sx={{
                  height: 52,
                  '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                  '&:hover': { bgcolor: '#F0F5FF' },
                }}
              >
                <TableCell sx={{ py: 1, px: 2.5 }}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 600,
                      fontSize: 13,
                      color: '#0D2144',
                    }}
                  >
                    {p.pipeline_name}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#4B6080' }}>
                    {p.total_deals}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#00A8E8', fontWeight: 600 }}>
                    {p.open_deals}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#10B981', fontWeight: 600 }}>
                    {p.won_deals}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#EF4444', fontWeight: 600 }}>
                    {p.lost_deals}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#0D2144' }}>
                    {fmt(p.pipeline_value)}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#10B981', fontWeight: 600 }}>
                    {fmt(p.won_revenue)}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Box
                    sx={{
                      display: 'inline-flex',
                      px: 1,
                      py: 0.3,
                      borderRadius: '20px',
                      bgcolor: p.win_rate >= 50
                        ? 'rgba(16,185,129,0.12)'
                        : 'rgba(245,158,11,0.12)',
                      color: p.win_rate >= 50 ? '#059669' : '#D97706',
                      fontFamily: 'Inter',
                      fontSize: 12,
                      fontWeight: 700,
                    }}
                  >
                    {p.win_rate.toFixed(1)}%
                  </Box>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#4B6080' }}>
                    {fmt(p.avg_deal_size)}
                  </Typography>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Box>
  );
}

/* ── Main page ── */
export default function AnalyticsPage() {
  const { t } = useTranslation();

  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [forecast, setForecast] = useState<RevenueForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ov, fc] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getForecast(),
      ]);
      setOverview(ov);
      setForecast(fc);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <Box>
      {/* ── Header ── */}
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
              color: '#0D2144',
              lineHeight: 1.2,
            }}
          >
            {t('analytics.title')}
          </Typography>
          <Typography sx={{ fontSize: 14, color: '#4B6080', mt: 0.5 }}>
            {t('analytics.greeting')}
          </Typography>
        </Box>
        <Tooltip title={t('analytics.refresh')}>
          <IconButton
            onClick={load}
            disabled={loading}
            size="small"
            sx={{
              border: '1px solid #E2EAF4',
              borderRadius: '10px',
              color: '#4B6080',
              '&:hover': { bgcolor: '#F0F5FF' },
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
            label={t('analytics.kpi.winRate')}
            value={overview ? `${overview.overall_win_rate.toFixed(1)}%` : '—'}
            icon={<ShowChartIcon fontSize="small" />}
            accentColor="#10B981"
            subtext={overview ? t('analytics.kpi.ofDeals', { count: overview.total_deals }) : undefined}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('analytics.kpi.avgDealSize')}
            value={overview ? fmt(overview.avg_deal_size) : '—'}
            icon={<WorkIcon fontSize="small" />}
            accentColor="#00A8E8"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('analytics.kpi.closedRevenue')}
            value={forecast ? fmt(forecast.closed_revenue) : '—'}
            icon={<AttachMoneyIcon fontSize="small" />}
            accentColor="#0D2144"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label={t('analytics.kpi.weightedForecast')}
            value={forecast ? fmt(forecast.weighted_forecast) : '—'}
            icon={<TrendingUpIcon fontSize="small" />}
            accentColor="#F59E0B"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* ── Row 2: Funnel + Forecast ── */}
      <Grid container spacing={2.5} sx={{ mb: 2.5 }}>
        <Grid item xs={12} md={7}>
          <ConversionFunnelCard overview={overview} loading={loading} />
        </Grid>
        <Grid item xs={12} md={5}>
          <RevenueForecastCard forecast={forecast} loading={loading} />
        </Grid>
      </Grid>

      {/* ── Row 3: Pipeline stats table ── */}
      <PipelineStatsTable overview={overview} loading={loading} />
    </Box>
  );
}
