import { Box, Card, Skeleton, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { LeadsStatusBreakdown } from '../../types/analytics';

interface LeadsStatusChartProps {
  data: LeadsStatusBreakdown | null;
  loading: boolean;
}

const CARD_STYLE = {
  height: '100%',
  bgcolor: 'background.paper',
  border: '1px solid', borderColor: 'divider',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

const SLICE_COLORS = ['#00A8E8', '#F59E0B', '#10B981', '#EF4444', '#0D2144'];

export default function LeadsStatusChart({ data, loading }: LeadsStatusChartProps) {
  const { t } = useTranslation();

  const SLICES = data
    ? [
        { name: t('dashboard.charts.new'), value: data.new, color: SLICE_COLORS[0] },
        { name: t('dashboard.charts.contacted'), value: data.contacted, color: SLICE_COLORS[1] },
        { name: t('dashboard.charts.qualified'), value: data.qualified, color: SLICE_COLORS[2] },
        { name: t('dashboard.charts.unqualified'), value: data.unqualified, color: SLICE_COLORS[3] },
        { name: t('dashboard.charts.converted'), value: data.converted, color: SLICE_COLORS[4] },
      ].filter((s) => s.value > 0)
    : [];

  const total = SLICES.reduce((sum, s) => sum + s.value, 0);

  return (
    <Card elevation={0} sx={CARD_STYLE}>
      <Box sx={{ p: 2.5 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 15,
            color: 'text.primary',
            mb: 2,
          }}
        >
          {t('dashboard.charts.leadsByStatus')}
        </Typography>

        {loading ? (
          <Skeleton variant="circular" width={200} height={200} sx={{ mx: 'auto' }} />
        ) : total === 0 ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: 240,
            }}
          >
            <Typography sx={{ fontSize: 13, color: '#94A3B8' }}>
              {t('dashboard.charts.noLeads')}
            </Typography>
          </Box>
        ) : (
          <Box sx={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={SLICES}
                  cx="50%"
                  cy="45%"
                  innerRadius={58}
                  outerRadius={88}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {SLICES.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, name: string) => [value, name]}
                  contentStyle={{
                    background: '#0D2144',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#FFFFFF',
                    fontSize: 12,
                    fontFamily: 'Inter, sans-serif',
                  }}
                  itemStyle={{ color: '#FFFFFF' }}
                  labelStyle={{ color: '#94A3B8' }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{
                    fontSize: 12,
                    fontFamily: 'Inter, sans-serif',
                    color: 'text.secondary',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        )}
      </Box>
    </Card>
  );
}
