import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import CallIcon from '@mui/icons-material/Call';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EmailIcon from '@mui/icons-material/Email';
import EventIcon from '@mui/icons-material/Event';
import NoteIcon from '@mui/icons-material/Note';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import {
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  InputBase,
  Skeleton,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { dealsApi } from '../../api/deals';
import { type Activity, type ActivityType } from '../../types/activity';
import { type Deal } from '../../types/deal';

/* ── Activity type config (mirrors ActivityTimeline) ── */
const ACTIVITY_META: Record<ActivityType, { icon: React.ReactNode; color: string; bg: string }> = {
  call:           { icon: <CallIcon sx={{ fontSize: 14 }} />,        color: '#00A8E8', bg: 'rgba(0,168,232,0.12)' },
  email:          { icon: <EmailIcon sx={{ fontSize: 14 }} />,       color: '#8B5CF6', bg: 'rgba(139,92,246,0.12)' },
  meeting:        { icon: <EventIcon sx={{ fontSize: 14 }} />,       color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
  note:           { icon: <NoteIcon sx={{ fontSize: 14 }} />,        color: '#94A3B8', bg: 'rgba(148,163,184,0.12)' },
  status_change:  { icon: <SwapHorizIcon sx={{ fontSize: 14 }} />,   color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
  stage_change:   { icon: <SwapHorizIcon sx={{ fontSize: 14 }} />,   color: 'text.primary', bg: 'rgba(13,33,68,0.10)' },
  lead_converted: { icon: <CheckCircleIcon sx={{ fontSize: 14 }} />, color: '#10B981', bg: 'rgba(16,185,129,0.12)' },
};

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

function ActivityEntry({ activity, isLast }: { activity: Activity; isLast: boolean }) {
  const { t } = useTranslation();
  const meta = ACTIVITY_META[activity.activity_type];
  return (
    <Box sx={{ display: 'flex', gap: 1.5 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
        <Box sx={{ width: 28, height: 28, borderRadius: '50%', bgcolor: meta.bg, color: meta.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {meta.icon}
        </Box>
        {!isLast && (
          <Box sx={{ width: '2px', flex: 1, minHeight: 20, background: 'repeating-linear-gradient(to bottom,#E2EAF4 0px,#E2EAF4 4px,transparent 4px,transparent 8px)', mt: 0.5 }} />
        )}
      </Box>
      <Box sx={{ pb: isLast ? 0 : 2.5, flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 1, mb: 0.25 }}>
          <Typography sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary', fontFamily: 'Inter, sans-serif' }}>
            {t(`leadDetail.timeline.types.${activity.activity_type}`)}
          </Typography>
          <Typography sx={{ fontSize: 11, color: '#94A3B8', flexShrink: 0, fontFamily: 'Inter, sans-serif' }}>
            {relativeTime(activity.occurred_at, (k, o) => t(k, o as Record<string, unknown>))}
          </Typography>
        </Box>
        {activity.body && (
          <Typography sx={{ fontSize: 13, color: 'text.secondary', lineHeight: 1.5, fontFamily: 'Inter, sans-serif' }}>
            {activity.body}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

interface Props {
  deal: Deal | null;
  open: boolean;
  onClose: () => void;
}

export default function DealActivitiesDialog({ deal, open, onClose }: Props) {
  const { t } = useTranslation();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open || !deal) return;
    setLoading(true);
    dealsApi.getActivities(deal.id)
      .then(setActivities)
      .finally(() => setLoading(false));
  }, [open, deal]);

  const handleSubmit = async () => {
    const trimmed = comment.trim();
    if (!trimmed || !deal || submitting) return;
    setSubmitting(true);
    try {
      const newActivity = await dealsApi.addComment(deal.id, trimmed);
      setActivities((prev) => [newActivity, ...prev]);
      setComment('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: '16px' } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 16, color: 'text.primary', pb: 1 }}>
        <Box>
          <Box>{t('deals.comments.title')}</Box>
          {deal && (
            <Typography sx={{ fontSize: 12, color: '#94A3B8', fontWeight: 400, fontFamily: 'Inter, sans-serif' }}>
              {deal.title}
            </Typography>
          )}
        </Box>
        <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 1 }}>
        {/* Comment input */}
        <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1, border: '1px solid', borderColor: 'divider', borderRadius: '10px', px: 1.5, py: 1, bgcolor: 'background.default', mb: 2.5 }}>
          <InputBase
            multiline
            maxRows={4}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder={t('deals.comments.placeholder')}
            onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit(); }}
            sx={{ flex: 1, fontSize: 13, fontFamily: 'Inter, sans-serif', color: 'text.primary' }}
          />
          <IconButton size="small" onClick={handleSubmit} disabled={!comment.trim() || submitting} sx={{ color: '#00A8E8', '&:disabled': { color: '#CBD5E1' } }}>
            {submitting ? <CircularProgress size={16} /> : <SendIcon fontSize="small" />}
          </IconButton>
        </Box>

        {/* Timeline */}
        {loading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {[0, 1, 2].map((i) => (
              <Box key={i} sx={{ display: 'flex', gap: 1.5 }}>
                <Skeleton variant="circular" width={28} height={28} sx={{ flexShrink: 0 }} />
                <Box sx={{ flex: 1 }}>
                  <Skeleton variant="text" width={120} height={16} />
                  <Skeleton variant="text" width="70%" height={14} />
                </Box>
              </Box>
            ))}
          </Box>
        )}

        {!loading && activities.length === 0 && (
          <Typography sx={{ textAlign: 'center', color: '#94A3B8', fontSize: 13, fontFamily: 'Inter, sans-serif', py: 2 }}>
            {t('deals.comments.empty')}
          </Typography>
        )}

        {!loading && activities.length > 0 && (
          <Box>
            {activities.map((a, idx) => (
              <ActivityEntry key={a.id} activity={a} isLast={idx === activities.length - 1} />
            ))}
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}
