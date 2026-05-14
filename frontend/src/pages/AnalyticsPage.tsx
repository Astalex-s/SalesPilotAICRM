import PeopleIcon from '@mui/icons-material/People';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import PrintIcon from '@mui/icons-material/Print';
import Chip from '@mui/material/Chip';
import {
  Alert,
  Box,
  Button,
  Grid,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import GlobalStyles from '@mui/material/GlobalStyles';
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
import { type AnalyticsOverview, type ManagerReportEntry, type ManagersReport, type RevenueForecast } from '../types/analytics';

/* ── Design tokens ── */
const CARD = {
  bgcolor: 'background.paper',
  border: '1px solid', borderColor: 'divider',
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
          color: 'text.primary',
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
          color: 'text.primary',
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
                  bgcolor: 'background.default',
                  border: '1px solid', borderColor: 'divider',
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
                      color: 'text.secondary',
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
                    color: 'text.primary',
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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

  /* Mobile card for a single pipeline stat */
  if (isMobile) {
    return (
      <Box sx={CARD}>
        <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
          <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 15, color: 'text.primary' }}>
            {t('analytics.pipelineStats.title')}
          </Typography>
        </Box>
        <Box sx={{ px: 2.5, pb: 2.5, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {loading ? (
            Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} variant="rounded" height={100} sx={{ borderRadius: '10px' }} />)
          ) : !overview || overview.pipeline_stats.length === 0 ? (
            <Typography sx={{ py: 4, textAlign: 'center', fontSize: 13, color: '#94A3B8' }}>{t('analytics.pipelineStats.noData')}</Typography>
          ) : (
            overview.pipeline_stats.map((p) => (
              <Box key={p.pipeline_id} sx={{ p: 2, borderRadius: '10px', bgcolor: 'background.default', border: '1px solid', borderColor: 'divider' }}>
                <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: 'text.primary', mb: 1 }}>{p.pipeline_name}</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 1 }}>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.open')}</Typography><Typography sx={{ fontSize: 14, fontWeight: 600, color: '#00A8E8' }}>{p.open_deals}</Typography></Box>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.won')}</Typography><Typography sx={{ fontSize: 14, fontWeight: 600, color: '#10B981' }}>{p.won_deals}</Typography></Box>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.lost')}</Typography><Typography sx={{ fontSize: 14, fontWeight: 600, color: '#EF4444' }}>{p.lost_deals}</Typography></Box>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.value')}</Typography><Typography sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary' }}>{fmt(p.pipeline_value)}</Typography></Box>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.revenue')}</Typography><Typography sx={{ fontSize: 13, fontWeight: 600, color: '#10B981' }}>{fmt(p.won_revenue)}</Typography></Box>
                  <Box><Typography sx={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase' }}>{t('analytics.pipelineStats.winRate')}</Typography><Typography sx={{ fontSize: 13, fontWeight: 700, color: p.win_rate >= 50 ? '#059669' : '#D97706' }}>{p.win_rate.toFixed(1)}%</Typography></Box>
                </Box>
              </Box>
            ))
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={CARD}>
      <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 15,
            color: 'text.primary',
          }}
        >
          {t('analytics.pipelineStats.title')}
        </Typography>
      </Box>

      <Table sx={{ tableLayout: 'fixed' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: 'action.hover' }}>
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
                  '&:hover': { bgcolor: 'action.hover' },
                }}
              >
                <TableCell sx={{ py: 1, px: 2.5 }}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 600,
                      fontSize: 13,
                      color: 'text.primary',
                    }}
                  >
                    {p.pipeline_name}
                  </Typography>
                </TableCell>
                <TableCell align="right" sx={{ py: 1, px: 2 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.secondary' }}>
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
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.primary' }}>
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
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.secondary' }}>
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

/* ── Managers Table ── */
const TH_SX = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 11,
  fontWeight: 500,
  letterSpacing: '0.07em',
  textTransform: 'uppercase' as const,
  color: '#94A3B8',
  border: 'none',
  py: 1.5,
  whiteSpace: 'nowrap',
};
const TD_SX = { border: 'none', borderTop: '1px solid #F0F5FF', py: 1.25 };

function ManagersTable({ report, loading }: { report: ManagersReport | null; loading: boolean }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const headerBlock = (
    <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
      <PeopleIcon sx={{ fontSize: 18, color: '#00A8E8' }} />
      <Box>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 15, color: 'text.primary' }}>
          {t('analytics.managers.title')}
        </Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>
          {t('analytics.managers.subtitle')}
        </Typography>
      </Box>
    </Box>
  );

  if (isMobile) {
    return (
      <Box sx={{ ...CARD, mt: 2.5 }}>
        {headerBlock}
        <Box sx={{ px: 2.5, pb: 2.5, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} variant="rounded" height={90} sx={{ borderRadius: '10px' }} />)
          ) : !report || report.managers.length === 0 ? (
            <Typography sx={{ py: 4, textAlign: 'center', fontSize: 14, color: '#94A3B8' }}>{t('analytics.managers.noData')}</Typography>
          ) : (
            report.managers.map((m: ManagerReportEntry) => (
              <Box key={m.manager_id} sx={{ p: 2, borderRadius: '10px', bgcolor: 'background.default', border: '1px solid', borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Box sx={{ minWidth: 0 }}>
                    <Typography noWrap sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: 'text.primary' }}>{m.manager_name}</Typography>
                    <Typography noWrap sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8' }}>{m.manager_email}</Typography>
                  </Box>
                  <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 14, color: 'text.primary', flexShrink: 0, ml: 1 }}>{fmt(m.won_revenue)}</Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  <Chip label={`${m.total_leads} ${t('analytics.managers.leads')}`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(13,33,68,0.06)', color: 'text.secondary' }} />
                  <Chip label={`${m.open_deals} open`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(0,168,232,0.1)', color: '#0090CC' }} />
                  <Chip label={`${m.won_deals} won`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(16,185,129,0.1)', color: '#059669' }} />
                  <Chip label={`WR ${m.win_rate.toFixed(0)}%`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: m.win_rate >= 50 ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: m.win_rate >= 50 ? '#059669' : '#D97706' }} />
                  {m.overdue_deals > 0 && <Chip label={`${m.overdue_deals} overdue`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(255,107,53,0.12)', color: '#FF6B35' }} />}
                </Box>
              </Box>
            ))
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ ...CARD, mt: 2.5 }}>
      {headerBlock}

      <Table sx={{ tableLayout: 'fixed' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: 'action.hover' }}>
            <TableCell sx={{ ...TH_SX, pl: 2.5 }}>{t('analytics.managers.manager')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 90 }}>{t('analytics.managers.leads')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 90 }}>{t('analytics.managers.conversion')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 200 }}>{t('analytics.managers.deals')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 90 }}>{t('analytics.managers.winRate')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 110 }}>{t('analytics.managers.revenue')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 110, pr: 2.5 }}>{t('analytics.managers.pipeline')}</TableCell>
            <TableCell sx={{ ...TH_SX, width: 80 }}>{t('analytics.managers.overdue')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <TableRow key={i}>
                {Array.from({ length: 8 }).map((__, j) => (
                  <TableCell key={j} sx={TD_SX}>
                    <Skeleton variant="text" width="80%" />
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : !report || report.managers.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center" sx={{ ...TD_SX, py: 6, fontFamily: 'Inter', fontSize: 14, color: '#94A3B8' }}>
                {t('analytics.managers.noData')}
              </TableCell>
            </TableRow>
          ) : (
            report.managers.map((m: ManagerReportEntry) => (
              <TableRow key={m.manager_id} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell sx={{ ...TD_SX, pl: 2.5 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 13, color: 'text.primary' }}>
                    {m.manager_name}
                  </Typography>
                  <Typography noWrap sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8' }}>
                    {m.manager_email}
                  </Typography>
                </TableCell>
                <TableCell sx={TD_SX}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.secondary' }}>
                    {m.total_leads}
                  </Typography>
                </TableCell>
                <TableCell sx={TD_SX}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: m.conversion_rate >= 20 ? '#10B981' : '#4B6080' }}>
                    {m.conversion_rate.toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell sx={TD_SX}>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    <Chip label={`${m.open_deals} open`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(0,168,232,0.1)', color: '#0090CC', fontFamily: 'Inter' }} />
                    <Chip label={`${m.won_deals} won`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(16,185,129,0.1)', color: '#059669', fontFamily: 'Inter' }} />
                    {m.lost_deals > 0 && (
                      <Chip label={`${m.lost_deals} lost`} size="small" sx={{ fontSize: 10, height: 20, bgcolor: 'rgba(239,68,68,0.1)', color: '#DC2626', fontFamily: 'Inter' }} />
                    )}
                  </Box>
                </TableCell>
                <TableCell sx={TD_SX}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: m.win_rate >= 50 ? '#10B981' : '#F59E0B' }}>
                    {m.win_rate.toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell sx={TD_SX}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: 'text.primary' }}>
                    {fmt(m.won_revenue)}
                  </Typography>
                </TableCell>
                <TableCell sx={{ ...TD_SX, pr: 2.5 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.secondary' }}>
                    {fmt(m.pipeline_value)}
                  </Typography>
                </TableCell>
                <TableCell sx={TD_SX}>
                  {m.overdue_deals > 0 ? (
                    <Chip label={m.overdue_deals} size="small" sx={{ fontSize: 11, height: 20, bgcolor: 'rgba(255,107,53,0.12)', color: '#FF6B35', fontWeight: 700, fontFamily: 'Inter' }} />
                  ) : (
                    <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#CBD5E8' }}>—</Typography>
                  )}
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
  const [managers, setManagers] = useState<ManagersReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportAnchor, setExportAnchor] = useState<null | HTMLElement>(null);
  const [csvLoading, setCsvLoading] = useState(false);
  const downloadLinkRef = useRef<HTMLAnchorElement>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ov, fc, mgr] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getForecast(),
        analyticsApi.getManagersReport(),
      ]);
      setOverview(ov);
      setForecast(fc);
      setManagers(mgr);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCsvDownload = async () => {
    setExportAnchor(null);
    setCsvLoading(true);
    try {
      const blob = await analyticsApi.exportCsv();
      const url = URL.createObjectURL(blob);
      const a = downloadLinkRef.current!;
      a.href = url;
      a.download = `analytics_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silently ignore — user sees no data change
    } finally {
      setCsvLoading(false);
    }
  };

  const handlePrint = () => {
    setExportAnchor(null);
    window.print();
  };

  return (
    <Box>
      <GlobalStyles styles={{
        '@media print': {
          'header, nav, aside, [data-testid="sidebar"], [data-testid="topbar"]': { display: 'none !important' },
          '#root > div > div:first-of-type': { display: 'none !important' }, // sidebar
          body: { background: '#fff !important' },
          '.MuiDrawer-root, .MuiAppBar-root': { display: 'none !important' },
        },
      }} />

      {/* Hidden anchor for CSV download */}
      {/* eslint-disable-next-line jsx-a11y/anchor-has-content */}
      <a ref={downloadLinkRef} style={{ display: 'none' }} />

      {/* ── Header ── */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          mb: 3,
          flexWrap: 'wrap',
          gap: 1.5,
        }}
      >
        <Box>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: { xs: 20, md: 24 },
              fontWeight: 700,
              color: 'text.primary',
              lineHeight: 1.2,
            }}
          >
            {t('analytics.title')}
          </Typography>
          <Typography sx={{ fontSize: 14, color: 'text.secondary', mt: 0.5 }}>
            {t('analytics.greeting')}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button
            size="small"
            variant="outlined"
            startIcon={<MonitorHeartIcon fontSize="small" />}
            component="a"
            href="/grafana/"
            target="_blank"
            rel="noopener"
            sx={{
              borderColor: 'divider',
              color: 'text.secondary',
              borderRadius: '10px',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 500,
              fontSize: 13,
              textTransform: 'none',
              '&:hover': { bgcolor: 'action.hover', borderColor: '#C8D8F0' },
            }}
          >
            Grafana
          </Button>

          <Tooltip title={t('analytics.refresh')}>
            <IconButton
              onClick={load}
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

          <Button
            size="small"
            variant="outlined"
            startIcon={<FileDownloadIcon fontSize="small" />}
            onClick={(e) => setExportAnchor(e.currentTarget)}
            disabled={loading}
            sx={{
              borderColor: 'divider',
              color: 'text.secondary',
              borderRadius: '10px',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 500,
              fontSize: 13,
              textTransform: 'none',
              '&:hover': { bgcolor: 'action.hover', borderColor: '#C8D8F0' },
            }}
          >
            {csvLoading ? t('analytics.export.downloading') : t('analytics.export.button')}
          </Button>

          <Menu
            anchorEl={exportAnchor}
            open={Boolean(exportAnchor)}
            onClose={() => setExportAnchor(null)}
            PaperProps={{
              sx: {
                borderRadius: '12px',
                border: '1px solid', borderColor: 'divider',
                boxShadow: '0 8px 24px rgba(13,33,68,0.10)',
                mt: 0.5,
                minWidth: 160,
              },
            }}
          >
            <MenuItem onClick={handleCsvDownload} sx={{ gap: 1, py: 1.25 }}>
              <ListItemIcon sx={{ minWidth: 28 }}>
                <FileDownloadIcon fontSize="small" sx={{ color: '#00A8E8' }} />
              </ListItemIcon>
              <ListItemText
                primary={t('analytics.export.csv')}
                primaryTypographyProps={{ fontFamily: 'Inter', fontSize: 13 }}
              />
            </MenuItem>
            <MenuItem onClick={handlePrint} sx={{ gap: 1, py: 1.25 }}>
              <ListItemIcon sx={{ minWidth: 28 }}>
                <PrintIcon fontSize="small" sx={{ color: '#8B5CF6' }} />
              </ListItemIcon>
              <ListItemText
                primary={t('analytics.export.pdf')}
                primaryTypographyProps={{ fontFamily: 'Inter', fontSize: 13 }}
              />
            </MenuItem>
          </Menu>
        </Box>
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

      {/* ── Row 4: Managers report table ── */}
      <ManagersTable report={managers} loading={loading} />
    </Box>
  );
}
