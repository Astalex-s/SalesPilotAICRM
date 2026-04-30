import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Alert, Box, Grid, IconButton, Skeleton, Tooltip, Typography } from '@mui/material';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import AIBlock from '../components/lead/AIBlock';
import ActivityTimeline from '../components/lead/ActivityTimeline';
import LeadInfoCard from '../components/lead/LeadInfoCard';
import { useLeadDetailStore } from '../store/useLeadDetailStore';

export default function LeadDetailPage() {
  const { t } = useTranslation();
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();

  const {
    lead, activities, score, nextAction, generatedEmail,
    fetchLead, fetchActivities, fetchScore, fetchNextAction, generateEmail,
    reset,
  } = useLeadDetailStore();

  useEffect(() => {
    if (!leadId) return;
    fetchLead(leadId);
    fetchActivities(leadId);
    return () => { reset(); };
  }, [leadId, fetchLead, fetchActivities, reset]);

  if (lead.error) {
    return (
      <Alert severity="error" sx={{ borderRadius: '12px' }}>
        {lead.error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* ── Page header ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Tooltip title={t('leadDetail.back')}>
          <IconButton
            onClick={() => navigate('/leads')}
            size="small"
            sx={{
              border: '1px solid #E2EAF4',
              borderRadius: '10px',
              color: '#4B6080',
              '&:hover': { bgcolor: '#F0F5FF' },
            }}
          >
            <ArrowBackIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        {lead.loading ? (
          <Skeleton variant="text" width={200} height={32} />
        ) : lead.data ? (
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 24,
              fontWeight: 700,
              color: '#0D2144',
              lineHeight: 1.2,
            }}
          >
            {lead.data.first_name} {lead.data.last_name}
          </Typography>
        ) : null}
      </Box>

      {/* ── 3-column layout ── */}
      <Grid container spacing={2.5} alignItems="flex-start">
        {/* Left — profile card */}
        <Grid item xs={12} md={3}>
          {lead.loading ? (
            <Skeleton variant="rounded" height={420} sx={{ borderRadius: '16px' }} />
          ) : lead.data ? (
            <LeadInfoCard lead={lead.data} />
          ) : null}
        </Grid>

        {/* Center — activity timeline */}
        <Grid item xs={12} md={5}>
          <ActivityTimeline
            activities={activities.data ?? []}
            loading={activities.loading}
            error={activities.error}
          />
        </Grid>

        {/* Right — AI panel */}
        <Grid item xs={12} md={4}>
          <AIBlock
            score={score.data}
            scoreLoading={score.loading}
            scoreError={score.error}
            nextAction={nextAction.data}
            nextActionLoading={nextAction.loading}
            nextActionError={nextAction.error}
            generatedEmail={generatedEmail.data}
            emailLoading={generatedEmail.loading}
            emailError={generatedEmail.error}
            onScoreRefresh={() => leadId && fetchScore(leadId)}
            onNextActionRefresh={() => leadId && fetchNextAction(leadId)}
            onGenerateEmail={(tone, ctx) => leadId && generateEmail(leadId, tone, ctx || undefined)}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
