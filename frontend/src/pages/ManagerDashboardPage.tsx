import GroupsIcon from '@mui/icons-material/Groups';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import {
  Alert,
  Box,
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
import { analyticsApi } from '../api/analytics';
import { type ManagerReportEntry, type ManagersReport } from '../types/analytics';

/* ── Tokens ── */
const CARD_SX = {
  bgcolor: 'background.paper',
  border: '1px solid', borderColor: 'divider',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

const TH_SX = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: '0.07em',
  textTransform: 'uppercase' as const,
  color: '#94A3B8',
  border: 'none',
  py: 1.5,
  bgcolor: 'action.hover',
};

const BAR_COLORS = ['#00A8E8', '#7C3AED', '#10B981', '#F59E0B', '#EF4444', '#3B82F6'];

function fmt(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toFixed(0)}`;
}

/* ── KPI card ── */
function KpiCard({ label, value, sub, color }: { label: string; value: string; sub?: string; color: string }) {
  return (
    <Box sx={{ ...CARD_SX, p: 2.5, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 12, fontWeight: 600, letterSpacing: '0.06em', color: '#94A3B8', textTransform: 'uppercase' }}>
        {label}
      </Typography>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 26, fontWeight: 700, color, lineHeight: 1.1 }}>
        {value}
      </Typography>
      {sub && (
        <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>{sub}</Typography>
      )}
    </Box>
  );
}

/* ── Revenue bar chart ── */
function RevenueChart({ managers, loading }: { managers: ManagerReportEntry[]; loading: boolean }) {
  const { t } = useTranslation();
  const data = managers.map((m) => ({
    name: m.manager_name.split(' ')[0], // first name
    won: m.won_revenue,
    pipeline: m.pipeline_value,
  }));

  return (
    <Box sx={{ ...CARD_SX, p: 2.5 }}>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 15, fontWeight: 700, color: 'text.primary', mb: 0.5 }}>
        {t('managerDashboard.chart.title')}
      </Typography>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8', mb: 2.5 }}>
        {t('managerDashboard.chart.subtitle')}
      </Typography>
      {loading ? (
        <Skeleton variant="rounded" height={200} />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} barGap={4} barCategoryGap="35%">
            <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#E8EFF7" />
            <XAxis dataKey="name" tick={{ fontFamily: 'Inter', fontSize: 12, fill: '#5E6E82' }} axisLine={false} tickLine={false} />
            <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontFamily: 'Inter', fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
            <RTooltip
              formatter={(value: number, name: string) => [fmt(value), name === 'won' ? t('managerDashboard.chart.won') : t('managerDashboard.chart.pipeline')]}
              contentStyle={{ fontFamily: 'Inter', borderRadius: 10, border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 16px rgba(13,33,68,0.10)' }}
            />
            <Bar dataKey="won" radius={[6, 6, 0, 0]} name="won">
              {data.map((_, i) => (
                <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Box>
  );
}

/* ── Manager row ── */
function ManagerRow({ m }: { m: ManagerReportEntry }) {
  const { t } = useTranslation();
  const initials = m.manager_name.split(' ').map((p) => p[0] ?? '').join('').slice(0, 2).toUpperCase();
  const hasOverdue = m.overdue_deals > 0;

  return (
    <TableRow sx={{ '&:hover': { bgcolor: 'action.hover' }, '& td': { border: 'none', borderTop: '1px solid #F0F5FF' } }}>
      {/* Manager */}
      <TableCell sx={{ pl: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box sx={{ width: 34, height: 34, borderRadius: '50%', bgcolor: '#00A8E8', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', fontSize: 13, fontWeight: 700, flexShrink: 0 }}>
            {initials}
          </Box>
          <Box>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: 'text.primary', lineHeight: 1.2 }}>
              {m.manager_name}
            </Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>
              {m.manager_email}
            </Typography>
          </Box>
        </Box>
      </TableCell>

      {/* Leads */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: 'text.primary' }}>{m.total_leads}</Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>{m.converted_leads} {t('managerDashboard.table.converted')}</Typography>
      </TableCell>

      {/* Conv. rate */}
      <TableCell>
        <Box sx={{ display: 'inline-flex', px: 1.25, py: 0.4, borderRadius: '20px', bgcolor: 'rgba(16,185,129,0.10)', color: '#059669', fontFamily: 'Inter', fontSize: 12, fontWeight: 600 }}>
          {m.conversion_rate}%
        </Box>
      </TableCell>

      {/* Deals open/won/lost */}
      <TableCell>
        <Box sx={{ display: 'flex', gap: 0.75 }}>
          <Box sx={{ px: 1, py: 0.25, borderRadius: '6px', bgcolor: 'rgba(0,168,232,0.10)', color: '#0090CC', fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
            {m.open_deals} {t('managerDashboard.table.open')}
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: '6px', bgcolor: 'rgba(16,185,129,0.10)', color: '#059669', fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
            {m.won_deals} {t('managerDashboard.table.won')}
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: '6px', bgcolor: 'rgba(239,68,68,0.08)', color: '#DC2626', fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
            {m.lost_deals} {t('managerDashboard.table.lost')}
          </Box>
        </Box>
      </TableCell>

      {/* Win rate */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: m.win_rate >= 50 ? '#059669' : m.win_rate >= 30 ? '#D97706' : '#DC2626' }}>
          {m.win_rate}%
        </Typography>
      </TableCell>

      {/* Won revenue */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 700, color: 'text.primary' }}>
          {fmt(m.won_revenue)}
        </Typography>
      </TableCell>

      {/* Pipeline */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 14, color: '#5E6E82' }}>
          {fmt(m.pipeline_value)}
        </Typography>
      </TableCell>

      {/* Avg deal */}
      <TableCell>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#5E6E82' }}>
          {fmt(m.avg_deal_size)}
        </Typography>
      </TableCell>

      {/* Overdue */}
      <TableCell sx={{ pr: 2.5 }}>
        {hasOverdue ? (
          <Tooltip title={`${m.overdue_deals} ${t('managerDashboard.table.overdueDeals')}`}>
            <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5, px: 1.25, py: 0.4, borderRadius: '20px', bgcolor: 'rgba(245,158,11,0.12)', color: '#D97706', fontFamily: 'Inter', fontSize: 12, fontWeight: 600 }}>
              <WarningAmberIcon sx={{ fontSize: 13 }} />
              {m.overdue_deals}
            </Box>
          </Tooltip>
        ) : (
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>—</Typography>
        )}
      </TableCell>
    </TableRow>
  );
}

/* ── Main page ── */
export default function ManagerDashboardPage() {
  const { t } = useTranslation();
  const [report, setReport] = useState<ManagersReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await analyticsApi.getManagersReport();
      setReport(data);
    } catch {
      setError(t('managerDashboard.loadError'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  /* KPI aggregates */
  const managers = report?.managers ?? [];
  const totalWonRevenue = managers.reduce((s, m) => s + m.won_revenue, 0);
  const totalPipeline = managers.reduce((s, m) => s + m.pipeline_value, 0);
  const avgWinRate = managers.length
    ? managers.reduce((s, m) => s + m.win_rate, 0) / managers.length
    : 0;
  const totalOverdue = managers.reduce((s, m) => s + m.overdue_deals, 0);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: 'text.primary' }}>
            {t('managerDashboard.title')}
          </Typography>
          {!loading && report && (
            <Box sx={{ px: 1.5, py: 0.25, borderRadius: '20px', bgcolor: '#E8F4FF', color: '#00A8E8', fontFamily: 'Inter', fontSize: 13, fontWeight: 600 }}>
              {report.total_managers} {t('managerDashboard.managers')}
            </Box>
          )}
        </Box>
        <Tooltip title={t('managerDashboard.refresh')}>
          <IconButton onClick={load} disabled={loading} sx={{ color: '#5E6E82', '&:hover': { color: '#00A8E8', bgcolor: 'action.selected' } }}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

      {/* ── KPI cards ── */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2.5, mb: 3 }}>
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="rounded" height={100} sx={{ borderRadius: '16px' }} />
          ))
        ) : (
          <>
            <KpiCard
              label={t('managerDashboard.kpi.totalManagers')}
              value={String(report?.total_managers ?? 0)}
              sub={t('managerDashboard.kpi.activeReps')}
              color="#0D2144"
            />
            <KpiCard
              label={t('managerDashboard.kpi.wonRevenue')}
              value={fmt(totalWonRevenue)}
              sub={t('managerDashboard.kpi.closedDeals')}
              color="#059669"
            />
            <KpiCard
              label={t('managerDashboard.kpi.avgWinRate')}
              value={`${avgWinRate.toFixed(1)}%`}
              sub={t('managerDashboard.kpi.acrossTeam')}
              color={avgWinRate >= 50 ? '#059669' : '#D97706'}
            />
            <KpiCard
              label={t('managerDashboard.kpi.pipeline')}
              value={fmt(totalPipeline)}
              sub={totalOverdue > 0 ? `${totalOverdue} ${t('managerDashboard.kpi.overdueDeals')}` : t('managerDashboard.kpi.noOverdue')}
              color="#00A8E8"
            />
          </>
        )}
      </Box>

      {/* ── Chart + empty state grid ── */}
      {!loading && managers.length === 0 ? (
        <Box sx={{ ...CARD_SX, display: 'flex', flexDirection: 'column', alignItems: 'center', py: 10 }}>
          <GroupsIcon sx={{ fontSize: 56, color: '#CBD5E8', mb: 2 }} />
          <Typography sx={{ fontFamily: 'Inter', fontSize: 16, fontWeight: 600, color: 'text.secondary', mb: 0.5 }}>
            {t('managerDashboard.noData')}
          </Typography>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 14, color: '#94A3B8' }}>
            {t('managerDashboard.noDataSubtitle')}
          </Typography>
        </Box>
      ) : (
        <>
          {/* Revenue bar chart */}
          <Box sx={{ mb: 3 }}>
            <RevenueChart managers={managers} loading={loading} />
          </Box>

          {/* ── Manager table ── */}
          <Box sx={{ ...CARD_SX, overflowX: 'auto' }}>
            <Box sx={{ p: 2.5, borderBottom: '1px solid #EFF4FB' }}>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 15, fontWeight: 700, color: 'text.primary' }}>
                {t('managerDashboard.table.title')}
              </Typography>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8', mt: 0.25 }}>
                {t('managerDashboard.table.subtitle')}
              </Typography>
            </Box>
            <Table sx={{ tableLayout: 'auto' }}>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ ...TH_SX, pl: 2.5 }}>{t('managerDashboard.table.manager')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.leads')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.convRate')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.deals')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.winRate')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.wonRevenue')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.pipeline')}</TableCell>
                  <TableCell sx={TH_SX}>{t('managerDashboard.table.avgDeal')}</TableCell>
                  <TableCell sx={{ ...TH_SX, pr: 2.5 }}>{t('managerDashboard.table.overdue')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading
                  ? Array.from({ length: 4 }).map((_, i) => (
                      <TableRow key={i} sx={{ height: 64 }}>
                        {Array.from({ length: 9 }).map((__, j) => (
                          <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                            <Skeleton variant="text" width="80%" />
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  : managers.map((m) => <ManagerRow key={m.manager_id} m={m} />)
                }
              </TableBody>
            </Table>
          </Box>
        </>
      )}
    </Box>
  );
}
