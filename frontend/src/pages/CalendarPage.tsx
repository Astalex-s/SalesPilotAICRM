import AddIcon from '@mui/icons-material/Add';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Skeleton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import AddMeetingDialog from '../components/calendar/AddMeetingDialog';
import { useMeetingStore } from '../store/useMeetingStore';
import { type CrmMeeting, type MeetingStatus } from '../types/meeting';

/* ── Status style ─────────────────────────────────────────────────────────── */
const STATUS_STYLE: Record<MeetingStatus, { bg: string; color: string; label: string }> = {
  scheduled:  { bg: 'rgba(0,168,232,0.10)',   color: '#0090CC', label: 'Scheduled' },
  completed:  { bg: 'rgba(16,185,129,0.10)',  color: '#059669', label: 'Completed' },
  cancelled:  { bg: 'rgba(148,163,184,0.10)', color: '#64748B', label: 'Cancelled' },
};

const DOT_COLORS: Record<MeetingStatus, string> = {
  scheduled: '#00A8E8',
  completed: '#10B981',
  cancelled: '#94A3B8',
};

/* ── Helpers ──────────────────────────────────────────────────────────────── */
function isoToDateKey(iso: string): string {
  // "2026-05-15T10:00:00Z" → "2026-05-15"
  return iso.slice(0, 10);
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function formatDateLabel(date: Date): string {
  return date.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
}

function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstWeekday(year: number, month: number): number {
  // Monday=0 … Sunday=6
  const d = new Date(year, month, 1).getDay();
  return (d + 6) % 7;
}

function toYMD(year: number, month: number, day: number): string {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

/* ── Meeting row ──────────────────────────────────────────────────────────── */
function MeetingRow({ meeting, onComplete, onDelete }: {
  meeting: CrmMeeting;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  const { t } = useTranslation();
  const st = STATUS_STYLE[meeting.status];
  const [completing, setCompleting] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleComplete = async () => {
    setCompleting(true);
    try { await onComplete(meeting.id); } finally { setCompleting(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try { await onDelete(meeting.id); } finally { setDeleting(false); }
  };

  return (
    <Box sx={{
      display: 'flex', alignItems: 'flex-start', gap: 2,
      p: 2, borderRadius: '12px', bgcolor: '#F8FAFC',
      border: '1px solid #EFF4FB',
      '&:hover': { bgcolor: '#F0F5FF', borderColor: '#D1E3F8' },
    }}>
      {/* Time column */}
      <Box sx={{ minWidth: 80, flexShrink: 0 }}>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 700, color: '#0D2144', lineHeight: 1.2 }}>
          {formatTime(meeting.start_time)}
        </Typography>
        {meeting.end_time && (
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', lineHeight: 1.2 }}>
            {formatTime(meeting.end_time)}
          </Typography>
        )}
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: '#0D2144' }}>
            {meeting.title}
          </Typography>
          <Box sx={{ px: 1, py: 0.25, borderRadius: '20px', bgcolor: st.bg, color: st.color, fontFamily: 'Inter', fontSize: 11, fontWeight: 600 }}>
            {t(`calendar.status.${meeting.status}`)}
          </Box>
        </Box>
        {meeting.description && (
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#5E6E82', mt: 0.25 }}>
            {meeting.description.length > 80 ? meeting.description.slice(0, 80) + '…' : meeting.description}
          </Typography>
        )}
        {meeting.location && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5, color: '#94A3B8' }}>
            <LocationOnOutlinedIcon sx={{ fontSize: 14 }} />
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12 }}>{meeting.location}</Typography>
          </Box>
        )}
      </Box>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
        {meeting.status === 'scheduled' && (
          <Tooltip title={t('calendar.complete')}>
            <Box
              component="button"
              onClick={handleComplete}
              disabled={completing}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #D1FAE5', bgcolor: '#F0FDF4', color: '#10B981', cursor: 'pointer', '&:hover': { bgcolor: '#D1FAE5' }, '&:disabled': { opacity: 0.5, cursor: 'default' } }}
            >
              {completing ? <CircularProgress size={14} sx={{ color: '#10B981' }} /> : <CheckCircleOutlineIcon sx={{ fontSize: 15 }} />}
            </Box>
          </Tooltip>
        )}
        <Tooltip title={t('calendar.delete')}>
          <Box
            component="button"
            onClick={handleDelete}
            disabled={deleting}
            sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: '6px', border: '1px solid #FEE2E2', bgcolor: '#FFF5F5', color: '#EF4444', cursor: 'pointer', '&:hover': { bgcolor: '#FEE2E2' }, '&:disabled': { opacity: 0.5, cursor: 'default' } }}
          >
            {deleting ? <CircularProgress size={14} sx={{ color: '#EF4444' }} /> : <DeleteOutlineIcon sx={{ fontSize: 15 }} />}
          </Box>
        </Tooltip>
      </Box>
    </Box>
  );
}

/* ── Main page ────────────────────────────────────────────────────────────── */
export default function CalendarPage() {
  const { t } = useTranslation();
  const { meetings, loading, error, fetchMeetings, updateMeeting, deleteMeeting } = useMeetingStore();

  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth()); // 0-based
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => { fetchMeetings(); }, [fetchMeetings]);

  /* Map: date-key → meetings[] */
  const meetingsByDay = useMemo(() => {
    const map: Record<string, CrmMeeting[]> = {};
    for (const m of meetings) {
      const key = isoToDateKey(m.start_time);
      if (!map[key]) map[key] = [];
      map[key].push(m);
    }
    return map;
  }, [meetings]);

  /* Calendar grid */
  const daysInMonth = getDaysInMonth(viewYear, viewMonth);
  const firstWeekday = getFirstWeekday(viewYear, viewMonth);
  const todayKey = toYMD(today.getFullYear(), today.getMonth(), today.getDate());

  /* Displayed meetings (selected day or whole month) */
  const displayedMeetings = useMemo(() => {
    if (selectedDay) return meetingsByDay[selectedDay] ?? [];
    // Show whole current month sorted
    return meetings.filter((m) => {
      const key = isoToDateKey(m.start_time);
      return key.startsWith(`${viewYear}-${String(viewMonth + 1).padStart(2, '0')}`);
    });
  }, [meetings, meetingsByDay, selectedDay, viewYear, viewMonth]);

  const prevMonth = () => {
    if (viewMonth === 0) { setViewYear((y) => y - 1); setViewMonth(11); }
    else setViewMonth((m) => m - 1);
    setSelectedDay(null);
  };

  const nextMonth = () => {
    if (viewMonth === 11) { setViewYear((y) => y + 1); setViewMonth(0); }
    else setViewMonth((m) => m + 1);
    setSelectedDay(null);
  };

  const handleComplete = async (id: string) => {
    await updateMeeting(id, { status: 'completed' });
  };

  const handleDelete = async (id: string) => {
    await deleteMeeting(id);
  };

  const WEEKDAYS = [
    t('calendar.weekdays.mon'), t('calendar.weekdays.tue'),
    t('calendar.weekdays.wed'), t('calendar.weekdays.thu'),
    t('calendar.weekdays.fri'), t('calendar.weekdays.sat'),
    t('calendar.weekdays.sun'),
  ];

  const MONTH_NAMES = [
    t('calendar.months.jan'), t('calendar.months.feb'), t('calendar.months.mar'),
    t('calendar.months.apr'), t('calendar.months.may'), t('calendar.months.jun'),
    t('calendar.months.jul'), t('calendar.months.aug'), t('calendar.months.sep'),
    t('calendar.months.oct'), t('calendar.months.nov'), t('calendar.months.dec'),
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144' }}>
          {t('calendar.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{ bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14, borderRadius: '10px', px: 2.5, textTransform: 'none', boxShadow: 'none', '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' } }}
        >
          {t('calendar.addMeeting')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '340px 1fr' }, gap: 3, alignItems: 'start' }}>

        {/* ── Calendar grid ── */}
        <Box sx={{ bgcolor: '#FFFFFF', border: '1px solid #E2EAF4', borderRadius: '16px', p: 2.5, boxShadow: '0 4px 24px rgba(13,33,68,0.07)' }}>
          {/* Month nav */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box
              component="button"
              onClick={prevMonth}
              sx={{ border: 'none', bgcolor: 'transparent', cursor: 'pointer', color: '#5E6E82', display: 'flex', p: 0.5, borderRadius: '6px', '&:hover': { bgcolor: '#F0F5FF', color: '#00A8E8' } }}
            >
              <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M15 18l-6-6 6-6" /></svg>
            </Box>
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 15, fontWeight: 700, color: '#0D2144' }}>
              {MONTH_NAMES[viewMonth]} {viewYear}
            </Typography>
            <Box
              component="button"
              onClick={nextMonth}
              sx={{ border: 'none', bgcolor: 'transparent', cursor: 'pointer', color: '#5E6E82', display: 'flex', p: 0.5, borderRadius: '6px', '&:hover': { bgcolor: '#F0F5FF', color: '#00A8E8' } }}
            >
              <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 18l6-6-6-6" /></svg>
            </Box>
          </Box>

          {/* Weekday headers */}
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', mb: 0.5 }}>
            {WEEKDAYS.map((d) => (
              <Box key={d} sx={{ textAlign: 'center', py: 0.5, fontFamily: 'Inter', fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', color: '#94A3B8', textTransform: 'uppercase' }}>
                {d}
              </Box>
            ))}
          </Box>

          {/* Day cells */}
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 0.25 }}>
            {/* Empty cells for offset */}
            {Array.from({ length: firstWeekday }).map((_, i) => (
              <Box key={`empty-${i}`} />
            ))}

            {/* Day cells */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1;
              const key = toYMD(viewYear, viewMonth, day);
              const dayMeetings = meetingsByDay[key] ?? [];
              const isToday = key === todayKey;
              const isSelected = key === selectedDay;

              return (
                <Box
                  key={key}
                  onClick={() => setSelectedDay(isSelected ? null : key)}
                  sx={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center',
                    py: 0.75, px: 0.25, borderRadius: '8px', cursor: 'pointer',
                    bgcolor: isSelected ? '#00A8E8' : isToday ? '#E8F7FF' : 'transparent',
                    border: isToday && !isSelected ? '1px solid #00A8E8' : '1px solid transparent',
                    '&:hover': { bgcolor: isSelected ? '#0090CC' : '#F0F5FF' },
                    transition: 'background 0.1s',
                  }}
                >
                  <Typography sx={{
                    fontFamily: 'Inter', fontSize: 13, fontWeight: isToday || isSelected ? 700 : 400,
                    color: isSelected ? '#fff' : isToday ? '#00A8E8' : '#0D2144',
                    lineHeight: 1.2,
                  }}>
                    {day}
                  </Typography>
                  {/* Dots for meetings */}
                  {dayMeetings.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.25, mt: 0.3, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 28 }}>
                      {dayMeetings.slice(0, 3).map((m) => (
                        <Box
                          key={m.id}
                          sx={{
                            width: 5, height: 5, borderRadius: '50%',
                            bgcolor: isSelected ? 'rgba(255,255,255,0.8)' : DOT_COLORS[m.status],
                          }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              );
            })}
          </Box>

          {/* Legend */}
          <Box sx={{ display: 'flex', gap: 2, mt: 2, pt: 2, borderTop: '1px solid #EFF4FB', flexWrap: 'wrap' }}>
            {(['scheduled', 'completed', 'cancelled'] as const).map((s) => (
              <Box key={s} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 7, height: 7, borderRadius: '50%', bgcolor: DOT_COLORS[s], flexShrink: 0 }} />
                <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8' }}>
                  {t(`calendar.status.${s}`)}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* ── Meeting list ── */}
        <Box>
          {/* Section title */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 16, fontWeight: 700, color: '#0D2144' }}>
              {selectedDay
                ? formatDateLabel(new Date(selectedDay + 'T00:00:00'))
                : `${MONTH_NAMES[viewMonth]} ${viewYear}`}
            </Typography>
            {!loading && (
              <Box sx={{ px: 1.25, py: 0.2, borderRadius: '20px', bgcolor: '#E8F4FF', color: '#00A8E8', fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 600 }}>
                {displayedMeetings.length}
              </Box>
            )}
            {selectedDay && (
              <Box
                component="button"
                onClick={() => setSelectedDay(null)}
                sx={{ ml: 'auto', border: 'none', bgcolor: 'transparent', cursor: 'pointer', color: '#94A3B8', fontFamily: 'Inter, sans-serif', fontSize: 12, '&:hover': { color: '#00A8E8' } }}
              >
                {t('calendar.showAll')}
              </Box>
            )}
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} variant="rounded" height={80} sx={{ borderRadius: '12px' }} />
              ))}
            </Box>
          ) : displayedMeetings.length === 0 ? (
            <Box sx={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              py: 8, bgcolor: '#FFFFFF', border: '1px solid #E2EAF4', borderRadius: '16px',
              boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
            }}>
              {/* Calendar illustration */}
              <Box sx={{ mb: 2, color: '#CBD5E8' }}>
                <svg width={56} height={56} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </Box>
              <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 16, fontWeight: 600, color: '#4B6080', mb: 0.5 }}>
                {t('calendar.noMeetings')}
              </Typography>
              <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#94A3B8', mb: 2.5 }}>
                {t('calendar.noMeetingsSubtitle')}
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setDialogOpen(true)}
                sx={{ bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter, sans-serif', fontWeight: 600, textTransform: 'none', borderRadius: '10px', boxShadow: 'none', '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' } }}
              >
                {t('calendar.addMeeting')}
              </Button>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {displayedMeetings.map((meeting) => (
                <MeetingRow
                  key={meeting.id}
                  meeting={meeting}
                  onComplete={handleComplete}
                  onDelete={handleDelete}
                />
              ))}
            </Box>
          )}
        </Box>
      </Box>

      <AddMeetingDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        defaultDate={selectedDay ?? undefined}
      />
    </Box>
  );
}
