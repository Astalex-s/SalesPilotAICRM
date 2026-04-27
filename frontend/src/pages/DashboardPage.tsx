import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import PeopleIcon from '@mui/icons-material/People';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkIcon from '@mui/icons-material/Work';
import { Alert, Box, Grid, IconButton, Tooltip, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useEffect } from 'react';
import DealsStatusChart from '../components/dashboard/DealsStatusChart';
import LeadsStatusChart from '../components/dashboard/LeadsStatusChart';
import StatCard from '../components/dashboard/StatCard';
import { useDashboardStore } from '../store/useDashboardStore';

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

export default function DashboardPage() {
  const { data, loading, error, fetchDashboard } = useDashboardStore();

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return (
    <Box>
      {/* Page header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" fontWeight={700}>
          Дашборд
        </Typography>
        <Tooltip title="Обновить">
          <IconButton onClick={fetchDashboard} disabled={loading} size="small">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* KPI cards row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Всего лидов"
            value={data?.total_leads ?? '—'}
            icon={<PeopleIcon />}
            color="primary.main"
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Конверсия"
            value={data ? `${data.conversion_rate}%` : '—'}
            icon={<TrendingUpIcon />}
            color="success.main"
            subtext="лидов → конвертировано"
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Всего сделок"
            value={data?.total_deals ?? '—'}
            icon={<WorkIcon />}
            color="secondary.main"
            subtext={data ? `${data.open_deals} открытых` : undefined}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Стоимость воронки"
            value={data ? formatCurrency(data.pipeline_value) : '—'}
            icon={<AccountTreeIcon />}
            color="info.main"
            subtext="открытые сделки"
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Прогноз выручки"
            value={data ? formatCurrency(data.revenue_forecast) : '—'}
            icon={<ShowChartIcon />}
            color="warning.main"
            subtext="взвешен по этапам"
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatCard
            label="Выигранные сделки"
            value={data?.deals_by_status.won ?? '—'}
            icon={<AttachMoneyIcon />}
            color="success.dark"
            subtext={
              data && data.total_deals > 0
                ? `${Math.round((data.deals_by_status.won / data.total_deals) * 100)}% побед`
                : undefined
            }
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Charts row */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <DealsStatusChart data={data?.deals_by_status ?? null} loading={loading} />
        </Grid>
        <Grid item xs={12} md={6}>
          <LeadsStatusChart data={data?.leads_by_status ?? null} loading={loading} />
        </Grid>
      </Grid>
    </Box>
  );
}
