import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { Box, Card, Skeleton, Typography } from '@mui/material';
import type { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  subtext?: string;
  loading?: boolean;
  accentColor?: string;
  trend?: { value: number };
}

export default function StatCard({
  label,
  value,
  icon,
  subtext,
  loading = false,
  accentColor = '#00A8E8',
  trend,
}: StatCardProps) {
  const isPositive = trend ? trend.value >= 0 : null;

  return (
    <Card
      elevation={0}
      sx={{
        height: '100%',
        background: '#FFFFFF',
        border: '1px solid #E2EAF4',
        borderRadius: '16px',
        boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Left accent bar */}
      <Box
        sx={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: 4,
          bgcolor: accentColor,
        }}
      />

      <Box sx={{ p: '20px 20px 20px 24px' }}>
        {/* Top row: label + icon */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            mb: 1.5,
          }}
        >
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
              fontWeight: 500,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: '#94A3B8',
              lineHeight: 1.4,
            }}
          >
            {label}
          </Typography>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: '10px',
              bgcolor: `${accentColor}1A`,
              color: accentColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              ml: 1,
            }}
          >
            {icon}
          </Box>
        </Box>

        {/* Value */}
        {loading ? (
          <Skeleton variant="text" width={100} height={44} />
        ) : (
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 32,
              fontWeight: 700,
              color: '#0D2144',
              lineHeight: 1.1,
              mb: 0.75,
            }}
          >
            {value}
          </Typography>
        )}

        {/* Trend + subtext */}
        {!loading && (trend || subtext) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
            {trend && (
              <>
                {isPositive ? (
                  <TrendingUpIcon sx={{ fontSize: 13, color: '#10B981' }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 13, color: '#EF4444' }} />
                )}
                <Typography
                  sx={{
                    fontSize: 12,
                    fontWeight: 600,
                    color: isPositive ? '#10B981' : '#EF4444',
                  }}
                >
                  {trend.value > 0 ? '+' : ''}
                  {trend.value}%
                </Typography>
              </>
            )}
            {subtext && (
              <Typography sx={{ fontSize: 12, color: '#94A3B8' }}>
                {trend ? '\u00b7 ' : ''}
                {subtext}
              </Typography>
            )}
          </Box>
        )}
      </Box>
    </Card>
  );
}
