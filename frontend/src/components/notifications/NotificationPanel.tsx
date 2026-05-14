import { Box, Popover, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  useNotificationStore,
  type CRMNotification,
  type NotificationType,
} from '../../store/useNotificationStore';

/* ── Design tokens ───────────────────────────────────────────────────────────── */
const TYPE_COLOR: Record<NotificationType, string> = {
  email:  '#00A8E8',
  deal:   '#10B981',
  lead:   '#F59E0B',
  system: '#8B5CF6',
};

const TYPE_ICON: Record<NotificationType, string> = {
  email:  'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6',
  deal:   'M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z M7 7h.01',
  lead:   'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M9 11a4 4 0 100-8 4 4 0 000 8z',
  system: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
};

/* ── Inline SVG ─────────────────────────────────────────────────────────────── */
function SvgIcon({ d, size = 14, color }: { d: string; size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke={color ?? 'currentColor'} strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round">
      {d.split(' M').map((seg, i) => (
        <path key={i} d={i === 0 ? seg : 'M' + seg} />
      ))}
    </svg>
  );
}

/* ── Relative time ──────────────────────────────────────────────────────────── */
function useRelativeTime() {
  const { t } = useTranslation();
  return (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime();
    const mins  = Math.floor(diff / 60_000);
    const hours = Math.floor(diff / 3_600_000);
    const days  = Math.floor(diff / 86_400_000);
    if (mins  < 1)  return t('time.justNow');
    if (hours < 1)  return t('time.minutesAgo',  { count: mins });
    if (days  < 1)  return t('time.hoursAgo',    { count: hours });
    return t('time.daysAgo', { count: days });
  };
}

/* ── Single notification row ─────────────────────────────────────────────────── */
function NotifRow({ n }: { n: CRMNotification }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { markRead, dismiss } = useNotificationStore();
  const rel = useRelativeTime();
  const color = TYPE_COLOR[n.type];

  const handleClick = () => {
    markRead(n.id);
    if (n.link) navigate(n.link);
  };

  return (
    <Box
      onClick={handleClick}
      sx={{
        display: 'flex', alignItems: 'flex-start', gap: 1.5,
        px: 2, py: 1.5,
        bgcolor: n.read ? 'transparent' : 'rgba(0,168,232,0.04)',
        borderLeft: n.read ? '3px solid transparent' : `3px solid ${color}`,
        cursor: n.link ? 'pointer' : 'default',
        transition: 'background 0.15s',
        '&:hover': { bgcolor: 'action.hover' },
      }}
    >
      {/* Type icon circle */}
      <Box sx={{
        width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
        bgcolor: `${color}18`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        mt: '2px',
      }}>
        <SvgIcon d={TYPE_ICON[n.type]} size={14} color={color} />
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 1 }}>
          <Typography sx={{
            fontSize: 13, fontWeight: n.read ? 400 : 600,
            color: 'text.primary', fontFamily: 'Inter, sans-serif',
            lineHeight: 1.3,
          }}>
            {t(n.titleKey, n.params)}
          </Typography>
          {!n.read && (
            <Box sx={{
              width: 7, height: 7, borderRadius: '50%',
              bgcolor: color, flexShrink: 0, mt: '3px',
            }} />
          )}
        </Box>
        <Typography sx={{
          fontSize: 12, color: '#5E6E82',
          fontFamily: 'Inter, sans-serif', lineHeight: 1.4,
          mt: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {t(n.msgKey, n.params)}
        </Typography>
        <Typography sx={{
          fontSize: 11, color: '#8FA3B8',
          fontFamily: 'Inter, sans-serif', mt: '4px',
        }}>
          {rel(n.timestamp)}
        </Typography>
      </Box>

      {/* Dismiss */}
      <Box
        onClick={(e) => { e.stopPropagation(); dismiss(n.id); }}
        sx={{
          color: '#8FA3B8', cursor: 'pointer', flexShrink: 0,
          display: 'flex', p: '2px', borderRadius: '4px',
          '&:hover': { color: '#EF4444', bgcolor: '#FFF5F5' },
          mt: '2px',
        }}
      >
        <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </Box>
    </Box>
  );
}

/* ── NotificationPanel ───────────────────────────────────────────────────────── */
interface NotificationPanelProps {
  anchorEl: HTMLElement | null;
  onClose: () => void;
}

export default function NotificationPanel({ anchorEl, onClose }: NotificationPanelProps) {
  const { t } = useTranslation();
  const { notifications, markAllRead } = useNotificationStore();
  const unread = notifications.filter((n) => !n.read).length;
  const open = Boolean(anchorEl);

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      disableScrollLock
      PaperProps={{
        elevation: 0,
        sx: {
          width: 380,
          maxHeight: 520,
          mt: 1,
          border: '1px solid', borderColor: 'divider',
          borderRadius: '12px',
          boxShadow: '0 8px 32px rgba(13,33,68,0.12)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      {/* Header */}
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        px: 2.5, py: 2,
        borderBottom: '1px solid #E8EFF7',
        flexShrink: 0,
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography sx={{
            fontSize: 15, fontWeight: 700, color: 'text.primary',
            fontFamily: 'Inter, sans-serif',
          }}>
            {t('notifications.title')}
          </Typography>
          {unread > 0 && (
            <Box sx={{
              px: '7px', py: '2px', borderRadius: '999px',
              bgcolor: '#FF6B35', minWidth: 20,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Typography sx={{ fontSize: 10, fontWeight: 700, color: '#fff', fontFamily: 'Inter, sans-serif', lineHeight: 1 }}>
                {unread}
              </Typography>
            </Box>
          )}
        </Box>
        {unread > 0 && (
          <Box
            onClick={markAllRead}
            sx={{
              fontSize: 12, fontWeight: 500, color: '#00A8E8',
              fontFamily: 'Inter, sans-serif', cursor: 'pointer',
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            {t('notifications.markAllRead')}
          </Box>
        )}
      </Box>

      {/* List */}
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        {notifications.length === 0 ? (
          <Box sx={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            justifyContent: 'center', py: 6, gap: 1.5,
          }}>
            <Box sx={{
              width: 48, height: 48, borderRadius: '50%',
              bgcolor: 'action.selected',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width={24} height={24} viewBox="0 0 24 24" fill="none"
                stroke="#00A8E8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0" />
              </svg>
            </Box>
            <Typography sx={{ fontSize: 14, color: '#8FA3B8', fontFamily: 'Inter, sans-serif', fontWeight: 500 }}>
              {t('notifications.noMore')}
            </Typography>
          </Box>
        ) : (
          <Box>
            {notifications.map((n, i) => (
              <Box key={n.id}>
                <NotifRow n={n} />
                {i < notifications.length - 1 && (
                  <Box sx={{ height: 1, bgcolor: '#F3F6FA', mx: 2 }} />
                )}
              </Box>
            ))}
          </Box>
        )}
      </Box>

      {/* Footer */}
      {notifications.length > 0 && (
        <Box sx={{
          px: 2.5, py: 1.5,
          borderTop: '1px solid #E8EFF7',
          flexShrink: 0,
        }}>
          <Typography sx={{
            fontSize: 12, color: '#8FA3B8',
            fontFamily: 'Inter, sans-serif', textAlign: 'center',
          }}>
            {t('notifications.footer', { count: notifications.length })}
          </Typography>
        </Box>
      )}
    </Popover>
  );
}
