import { Box, Card, CardContent, Skeleton, Typography, useTheme } from '@mui/material';
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

export default function DealsStatusChart({ data, loading }: DealsStatusChartProps) {
  const theme = useTheme();

  const BAR_DATA = data
    ? [
        { name: 'Открытые', value: data.open, color: theme.palette.primary.main },
        { name: 'Выигранные', value: data.won, color: theme.palette.success.main },
        { name: 'Проигранные', value: data.lost, color: theme.palette.error.main },
      ]
    : [];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Сделки по статусу
        </Typography>
        {loading ? (
          <Skeleton variant="rectangular" height={220} />
        ) : (
          <Box sx={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={BAR_DATA} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => [value, 'Сделки']}
                  contentStyle={{ fontSize: 12 }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={60}>
                  {BAR_DATA.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
