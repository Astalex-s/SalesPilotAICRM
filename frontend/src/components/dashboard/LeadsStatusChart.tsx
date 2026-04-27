import { Box, Card, CardContent, Skeleton, Typography, useTheme } from '@mui/material';
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { LeadsStatusBreakdown } from '../../types/analytics';

interface LeadsStatusChartProps {
  data: LeadsStatusBreakdown | null;
  loading: boolean;
}

export default function LeadsStatusChart({ data, loading }: LeadsStatusChartProps) {
  const theme = useTheme();

  const SLICES = data
    ? [
        { name: 'Новые', value: data.new, color: theme.palette.info.main },
        { name: 'Контакт', value: data.contacted, color: theme.palette.warning.main },
        { name: 'Квалифицир.', value: data.qualified, color: theme.palette.success.light },
        { name: 'Неквалифиц.', value: data.unqualified, color: theme.palette.error.light },
        { name: 'Конвертированы', value: data.converted, color: theme.palette.success.dark },
      ].filter((s) => s.value > 0)
    : [];

  const total = SLICES.reduce((sum, s) => sum + s.value, 0);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Лиды по статусу
        </Typography>
        {loading ? (
          <Skeleton variant="circular" width={220} height={220} sx={{ mx: 'auto' }} />
        ) : total === 0 ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 220 }}>
            <Typography variant="body2" color="text.secondary">
              Лидов пока нет
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
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {SLICES.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, name: string) => [value, name]}
                  contentStyle={{ fontSize: 12 }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: 12 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
