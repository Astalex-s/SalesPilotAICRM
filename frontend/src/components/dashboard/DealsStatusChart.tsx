import { Box, Card, Skeleton, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DealsStatusBreakdown } from '../../types/analytics';

interface DealsStatusChartProps {
  data: DealsStatusBreakdown | null;
  loading: boolean;
}

const CARD_STYLE = {
  height: '100%',
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

const COLORS = {
  open: '#00A8E8',
  won: '#10B981',
  lost: '#EF4444',
};

export default function DealsStatusChart({ data, loading }: DealsStatusChartProps) {
  const { t } = useTranslation();

  const BAR_DATA = data
    ? [
        { name: t('dashboard.charts.open'), value: data.open, color: COLORS.open },
        { name: t('dashboard.charts.won'), value: data.won, color: COLORS.won },
        { name: t('dashboard.charts.lost'), value: data.lost, color: COLORS.lost },
      ]
    : [];

  return (
    <Card elevation={0} sx={CARD_STYLE}>
      <Box sx={{ p: 2.5 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 15,
            color: '#0D2144',
            mb: 2,
          }}
        >
          {t('dashboard.charts.dealsByStatus')}
        </Typography>

        {loading ? (
          <Skeleton variant="rounded" height={220} sx={{ borderRadius: '10px' }} />
        ) : (
          <Box sx={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={BAR_DATA} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#E2EAF4"
                />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: '#4B6080', fontFamily: 'Inter, sans-serif' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 12, fill: '#94A3B8', fontFamily: 'Inter, sans-serif' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(value: number) => [value, t('dashboard.charts.deals')]}
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
                <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={72}>
                  {BAR_DATA.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        )}
      </Box>
    </Card>
  );
}
