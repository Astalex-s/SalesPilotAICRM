import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Alert, Box, Grid, IconButton, Skeleton, Tooltip, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { leadsApi } from '../api/leads';
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
    updateLead, addComment, reset,
  } = useLeadDetailStore();

  const [availableTags, setAvailableTags] = useState<string[]>([]);

  useEffect(() => {
    if (!leadId) return;
    fetchLead(leadId);
    fetchActivities(leadId);
    leadsApi.getTags().then(setAvailableTags).catch(() => {});
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
              border: '1px solid', borderColor: 'divider',
              borderRadius: '10px',
              color: 'text.secondary',
              '&:hover': { bgcolor: 'action.hover' },
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
              color: 'text.primary',
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
            <LeadInfoCard
              lead={lead.data}
              onStatusChange={(newStatus) => updateLead(lead.data!.id, { status: newStatus })}
              onTagsChange={(tags, category) => updateLead(lead.data!.id, { tags, category })}
              onDelete={async () => {
                if (!window.confirm(t('leadDetail.deleteConfirm'))) return;
                await leadsApi.delete(lead.data!.id);
                navigate('/leads');
              }}
              availableTags={availableTags}
            />
          ) : null}
        </Grid>

        {/* Center — activity timeline */}
        <Grid item xs={12} md={5}>
          <ActivityTimeline
            activities={activities.data ?? []}
            loading={activities.loading}
            error={activities.error}
            onAddComment={leadId ? (body) => addComment(leadId, body) : undefined}
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
            leadEmail={lead.data?.email}
            leadId={leadId}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
