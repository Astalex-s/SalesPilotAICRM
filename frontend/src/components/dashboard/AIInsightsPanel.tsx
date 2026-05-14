import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { Box, Card, Chip, Skeleton, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import type { DashboardAnalytics } from '../../types/analytics';

interface Insight {
  dotColor: string;
  title: string;
  desc: string;
  action: string;
}

function buildInsights(data: DashboardAnalytics, t: (k: string, o?: object) => string): Insight[] {
  const insights: Insight[] = [];

  if (data.deals_by_status.lost > 0) {
    insights.push({
      dotColor: '#F59E0B',
      title: t('dashboard.aiInsights.lostTitle', { count: data.deals_by_status.lost }),
      desc: t('dashboard.aiInsights.lostDesc'),
      action: t('dashboard.aiInsights.view'),
    });
  }

  if (data.conversion_rate > 0) {
    insights.push({
      dotColor: '#00A8E8',
      title: t('dashboard.aiInsights.winRateTitle', { rate: data.conversion_rate }),
      desc: t('dashboard.aiInsights.winRateDesc'),
      action: t('dashboard.aiInsights.view'),
    });
  }

  if (data.open_deals > 0) {
    insights.push({
      dotColor: '#10B981',
      title: t('dashboard.aiInsights.openDealsTitle', { count: data.open_deals }),
      desc: t('dashboard.aiInsights.openDealsDesc'),
      action: t('dashboard.aiInsights.view'),
    });
  }

  if (insights.length === 0) {
    insights.push({
      dotColor: '#10B981',
      title: t('dashboard.aiInsights.healthyTitle'),
      desc: t('dashboard.aiInsights.healthyDesc'),
      action: t('dashboard.aiInsights.view'),
    });
  }

  return insights.slice(0, 3);
}

interface AIInsightsPanelProps {
  data: DashboardAnalytics | null;
  loading?: boolean;
}

export default function AIInsightsPanel({ data, loading }: AIInsightsPanelProps) {
  const { t } = useTranslation();
  const insights = data ? buildInsights(data, (k, o) => t(k, o as Record<string, unknown>)) : [];

  return (
    <Card
      elevation={0}
      sx={{
        height: '100%',
        bgcolor: 'background.paper',
        border: '1px solid', borderColor: 'divider',
        borderRadius: '16px',
        boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
      }}
    >
      <Box sx={{ p: 2.5 }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2.5,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AutoAwesomeIcon sx={{ color: '#00A8E8', fontSize: 18 }} />
            <Typography
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 700,
                fontSize: 15,
                color: 'text.primary',
              }}
            >
              {t('dashboard.aiInsights.title')}
            </Typography>
          </Box>
          <Chip
            label="GPT-4"
            size="small"
            sx={{
              bgcolor: '#E8F4FF',
              color: '#00A8E8',
              fontWeight: 600,
              fontSize: 11,
              height: 22,
            }}
          />
        </Box>

        {/* Insights list */}
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            <Skeleton variant="rounded" height={72} sx={{ borderRadius: '10px' }} />
            <Skeleton variant="rounded" height={72} sx={{ borderRadius: '10px' }} />
            <Skeleton variant="rounded" height={72} sx={{ borderRadius: '10px' }} />
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {insights.map((insight, i) => (
              <Box
                key={i}
                sx={{
                  display: 'flex',
                  gap: 1.5,
                  p: 1.5,
                  borderRadius: '10px',
                  bgcolor: 'background.default',
                  border: '1px solid', borderColor: 'divider',
                }}
              >
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: insight.dotColor,
                    mt: '5px',
                    flexShrink: 0,
                  }}
                />
                <Box sx={{ flex: 1 }}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 600,
                      fontSize: 13,
                      color: 'text.primary',
                      mb: 0.25,
                    }}
                  >
                    {insight.title}
                  </Typography>
                  <Typography sx={{ fontSize: 12, color: '#94A3B8', lineHeight: 1.4 }}>
                    {insight.desc}
                  </Typography>
                  <Box
                    component="button"
                    sx={{
                      mt: 0.75,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 0.25,
                      fontSize: 12,
                      fontWeight: 600,
                      color: '#00A8E8',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      p: 0,
                      fontFamily: 'Inter, sans-serif',
                      '&:hover': { textDecoration: 'underline' },
                    }}
                  >
                    {insight.action}
                    <ArrowForwardIcon sx={{ fontSize: 12 }} />
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Card>
  );
}
