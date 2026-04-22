import CallIcon from '@mui/icons-material/Call';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EmailIcon from '@mui/icons-material/Email';
import EventIcon from '@mui/icons-material/Event';
import NoteIcon from '@mui/icons-material/Note';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import {
  Timeline,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineItem,
  TimelineOppositeContent,
  TimelineSeparator,
} from '@mui/lab';
import { Box, Card, CardContent, CircularProgress, Typography } from '@mui/material';
import { type Activity, type ActivityType } from '../../types/activity';

const ACTIVITY_META: Record<
  ActivityType,
  { icon: React.ReactNode; color: 'primary' | 'success' | 'warning' | 'info' | 'error' | 'grey' }
> = {
  call: { icon: <CallIcon fontSize="small" />, color: 'primary' },
  email: { icon: <EmailIcon fontSize="small" />, color: 'info' },
  meeting: { icon: <EventIcon fontSize="small" />, color: 'warning' },
  note: { icon: <NoteIcon fontSize="small" />, color: 'grey' },
  status_change: { icon: <SwapHorizIcon fontSize="small" />, color: 'warning' },
  stage_change: { icon: <SwapHorizIcon fontSize="small" />, color: 'primary' },
  lead_converted: { icon: <CheckCircleIcon fontSize="small" />, color: 'success' },
};

interface ActivityTimelineProps {
  activities: Activity[];
  loading: boolean;
  error: string | null;
}

export default function ActivityTimeline({ activities, loading, error }: ActivityTimelineProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={1}>
          Activity Timeline
        </Typography>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress size={28} />
          </Box>
        )}

        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}

        {!loading && !error && activities.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No activity yet.
          </Typography>
        )}

        {!loading && activities.length > 0 && (
          <Timeline sx={{ p: 0, m: 0 }}>
            {activities.map((activity, idx) => {
              const meta = ACTIVITY_META[activity.activity_type];
              return (
                <TimelineItem key={activity.id}>
                  <TimelineOppositeContent
                    sx={{ flex: 0.25, pr: 1 }}
                    variant="caption"
                    color="text.secondary"
                  >
                    {new Date(activity.occurred_at).toLocaleDateString()}
                    <br />
                    {new Date(activity.occurred_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </TimelineOppositeContent>

                  <TimelineSeparator>
                    <TimelineDot color={meta.color} variant="outlined">
                      {meta.icon}
                    </TimelineDot>
                    {idx < activities.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>

                  <TimelineContent sx={{ pb: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {activity.activity_type.replace('_', ' ')}
                    </Typography>
                    <Typography variant="body2">{activity.body}</Typography>
                  </TimelineContent>
                </TimelineItem>
              );
            })}
          </Timeline>
        )}
      </CardContent>
    </Card>
  );
}
