import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import {
  Alert,
  Box,
  CircularProgress,
  Grid,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import AIBlock from '../components/lead/AIBlock';
import ActivityTimeline from '../components/lead/ActivityTimeline';
import LeadInfoCard from '../components/lead/LeadInfoCard';
import { useLeadDetailStore } from '../store/useLeadDetailStore';

export default function LeadDetailPage() {
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

  if (lead.loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (lead.error) {
    return <Alert severity="error">{lead.error}</Alert>;
  }

  if (!lead.data) return null;

  return (
    <Box>
      {/* Page header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <Tooltip title="Back to Leads">
          <IconButton onClick={() => navigate('/leads')} size="small">
            <ArrowBackIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h4" fontWeight={700}>
          {lead.data.full_name}
        </Typography>
      </Box>

      <Grid container spacing={3} alignItems="flex-start">
        {/* Left column — info + timeline */}
        <Grid item xs={12} md={7}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <LeadInfoCard lead={lead.data} />
            <ActivityTimeline
              activities={activities.data ?? []}
              loading={activities.loading}
              error={activities.error}
            />
          </Box>
        </Grid>

        {/* Right column — AI block */}
        <Grid item xs={12} md={5}>
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
