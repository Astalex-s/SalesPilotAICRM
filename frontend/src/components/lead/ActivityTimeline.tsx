import EmptyState from '../common/EmptyState';
import CallIcon from '@mui/icons-material/Call';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EmailIcon from '@mui/icons-material/Email';
import EventIcon from '@mui/icons-material/Event';
import NoteIcon from '@mui/icons-material/Note';
import SendIcon from '@mui/icons-material/Send';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { Box, Card, CircularProgress, IconButton, InputBase, Skeleton, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { type Activity, type ActivityType } from '../../types/activity';

/* ── Activity type config ── */
const ACTIVITY_META: Record<
  ActivityType,
  { icon: React.ReactNode; color: string; bg: string }
> = {
  call:           { icon: <CallIcon sx={{ fontSize: 14 }} />,         color: '#00A8E8', bg: 'rgba(0,168,232,0.12)' },
  email:          { icon: <EmailIcon sx={{ fontSize: 14 }} />,        color: '#8B5CF6', bg: 'rgba(139,92,246,0.12)' },
  meeting:        { icon: <EventIcon sx={{ fontSize: 14 }} />,        color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
  note:           { icon: <NoteIcon sx={{ fontSize: 14 }} />,         color: '#94A3B8', bg: 'rgba(148,163,184,0.12)' },
  status_change:  { icon: <SwapHorizIcon sx={{ fontSize: 14 }} />,    color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
  stage_change:   { icon: <SwapHorizIcon sx={{ fontSize: 14 }} />,    color: '#0D2144', bg: 'rgba(13,33,68,0.10)' },
  lead_converted: { icon: <CheckCircleIcon sx={{ fontSize: 14 }} />,  color: '#10B981', bg: 'rgba(16,185,129,0.12)' },
};

/* ── Relative time ── */
function relativeTime(dateStr: string, t: (k: string, o?: object) => string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return t('time.justNow');
  if (mins < 60) return t('time.minutesAgo', { count: mins });
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return t('time.hoursAgo', { count: hrs });
  const days = Math.floor(hrs / 24);
  if (days < 7) return t('time.daysAgo', { count: days });
  return new Date(dateStr).toLocaleDateString(undefined, { day: '2-digit', month: 'short' });
}

/* ── Timeline item ── */
function TimelineEntry({
  activity,
  isLast,
}: {
  activity: Activity;
  isLast: boolean;
}) {
  const { t } = useTranslation();
  const meta = ACTIVITY_META[activity.activity_type];

  return (
    <Box sx={{ display: 'flex', gap: 1.5, position: 'relative' }}>
      {/* Icon column */}
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            bgcolor: meta.bg,
            color: meta.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          {meta.icon}
        </Box>
        {!isLast && (
          <Box
            sx={{
              width: '2px',
              flex: 1,
              minHeight: 24,
              background: `repeating-linear-gradient(
                to bottom,
                #E2EAF4 0px,
                #E2EAF4 4px,
                transparent 4px,
                transparent 8px
              )`,
              mt: 0.5,
            }}
          />
        )}
      </Box>

      {/* Content */}
      <Box sx={{ pb: isLast ? 0 : 2.5, flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 1, mb: 0.25 }}>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              fontWeight: 600,
              color: '#0D2144',
            }}
          >
            {t(`leadDetail.timeline.types.${activity.activity_type}`)}
          </Typography>
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
              color: '#94A3B8',
              flexShrink: 0,
            }}
          >
            {relativeTime(activity.occurred_at, (k, o) => t(k, o as Record<string, unknown>))}
          </Typography>
        </Box>
        {activity.body && (
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              color: '#4B6080',
              lineHeight: 1.5,
            }}
          >
            {activity.body}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

/* ── Skeleton ── */
function TimelineSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {Array.from({ length: 4 }).map((_, i) => (
        <Box key={i} sx={{ display: 'flex', gap: 1.5, mb: 2.5 }}>
          <Skeleton variant="circular" width={28} height={28} sx={{ flexShrink: 0 }} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width={120} height={18} />
            <Skeleton variant="text" width="80%" height={16} />
          </Box>
        </Box>
      ))}
    </Box>
  );
}

/* ── Comment input ── */
function CommentBox({ onSubmit }: { onSubmit: (body: string) => Promise<void> }) {
  const { t } = useTranslation();
  const [value, setValue] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    const trimmed = value.trim();
    if (!trimmed || submitting) return;
    setSubmitting(true);
    try {
      await onSubmit(trimmed);
      setValue('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        mt: 2,
        display: 'flex',
        alignItems: 'flex-end',
        gap: 1,
        border: '1px solid #E2EAF4',
        borderRadius: '10px',
        px: 1.5,
        py: 1,
        bgcolor: '#F7F9FC',
      }}
    >
      <InputBase
        multiline
        maxRows={4}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={t('leadDetail.timeline.commentPlaceholder')}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit();
        }}
        sx={{ flex: 1, fontSize: 13, fontFamily: 'Inter, sans-serif', color: '#0D2144' }}
      />
      <IconButton
        size="small"
        onClick={handleSubmit}
        disabled={!value.trim() || submitting}
        sx={{ color: '#00A8E8', '&:disabled': { color: '#CBD5E1' } }}
      >
        {submitting ? <CircularProgress size={16} /> : <SendIcon fontSize="small" />}
      </IconButton>
    </Box>
  );
}

/* ── Main component ── */
interface ActivityTimelineProps {
  activities: Activity[];
  loading: boolean;
  error: string | null;
  onAddComment?: (body: string) => Promise<void>;
}

export default function ActivityTimeline({ activities, loading, error, onAddComment }: ActivityTimelineProps) {
  const { t } = useTranslation();

  return (
    <Card
      elevation={0}
      sx={{
        background: '#FFFFFF',
        border: '1px solid #E2EAF4',
        borderRadius: '16px',
        boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
        height: '100%',
      }}
    >
      <Box sx={{ p: 2.5 }}>
        <Typography
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 15,
            color: '#0D2144',
            mb: 2.5,
          }}
        >
          {t('leadDetail.timeline.title')}
        </Typography>

        {loading && <TimelineSkeleton />}

        {error && (
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#EF4444' }}>
            {error}
          </Typography>
        )}

        {!loading && !error && activities.length === 0 && (
          <EmptyState
            icon="activity"
            title={t('leadDetail.timeline.empty')}
            subtitle={t('leadDetail.timeline.emptySubtitle')}
            compact
          />
        )}

        {!loading && activities.length > 0 && (
          <Box>
            {activities.map((activity, idx) => (
              <TimelineEntry
                key={activity.id}
                activity={activity}
                isLast={idx === activities.length - 1}
              />
            ))}
          </Box>
        )}

        {onAddComment && <CommentBox onSubmit={onAddComment} />}
      </Box>
    </Card>
  );
}
