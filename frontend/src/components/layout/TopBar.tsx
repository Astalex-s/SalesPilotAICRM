import { useEffect, useRef, useState } from 'react';
import { Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import {
  useNotificationStore,
  SEED_NOTIFICATIONS,
} from '../../store/useNotificationStore';
import { useUIStore } from '../../store/useUIStore';
import GlobalSearchModal from '../search/GlobalSearchModal';
import NotificationPanel from '../notifications/NotificationPanel';
import UserProfileDialog from '../profile/UserProfileDialog';

/* ── Inline language switcher ────────────────────────────────────────────────── */
function LangSwitcher() {
  const { i18n } = useTranslation();
  const current = i18n.language;
  const toggle = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('crm-lang', lang);
  };
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }}>
      {(['en', 'ru'] as const).map((lang) => (
        <Box
          key={lang}
          component="button"
          onClick={() => toggle(lang)}
          sx={{
            fontSize: 11, fontWeight: 600, fontFamily: 'Inter, sans-serif',
            border: 'none', background: 'none', cursor: 'pointer',
            px: '5px', py: '2px', borderRadius: '5px',
            color: current === lang ? '#00A8E8' : '#8FA3B8',
            bgcolor: current === lang ? 'rgba(0,168,232,0.1)' : 'transparent',
            transition: 'all 0.15s',
            '&:hover': { color: '#00A8E8' },
          }}
        >
          {lang.toUpperCase()}
        </Box>
      ))}
    </Box>
  );
}

/* ── Route → page title ──────────────────────────────────────────────────────── */
function usePageTitle() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  if (pathname === '/')                    return t('nav.dashboard');
  if (pathname.startsWith('/leads/'))     return t('nav.leadDetail');
  if (pathname === '/leads')              return t('nav.leads');
  if (pathname === '/deals')              return t('nav.deals');
  if (pathname.startsWith('/pipeline/')) return t('nav.pipeline');
  if (pathname === '/users')              return t('nav.admin');
  if (pathname === '/settings')           return t('nav.settings');
  return 'SalesPilotAI';
}

/* ── Bell icon SVG ───────────────────────────────────────────────────────────── */
function BellIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0" />
    </svg>
  );
}

/* ── Search icon ─────────────────────────────────────────────────────────────── */
function SearchIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

/* ── Avatar initials ─────────────────────────────────────────────────────────── */
function Avatar({ firstName, lastName }: { firstName: string; lastName: string }) {
  const theme = useTheme();
  const dark = theme.palette.mode === 'dark';
  const initials = `${firstName[0] ?? ''}${lastName[0] ?? ''}`.toUpperCase();
  const savedColor = localStorage.getItem('crm-avatar-color') ?? '#0D2144';
  return (
    <Box sx={{
      width: 32, height: 32, borderRadius: '50%',
      bgcolor: savedColor, color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 12, fontWeight: 700, fontFamily: 'Inter, sans-serif',
      border: dark ? '1.5px solid rgba(255,255,255,0.2)' : '1.5px solid #E8EFF7', flexShrink: 0,
    }}>
      {initials}
    </Box>
  );
}

/* ── Hamburger icon ──────────────────────────────────────────────────────────── */
function HamburgerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

/* ── TopBar ──────────────────────────────────────────────────────────────────── */
export default function TopBar() {
  const { t } = useTranslation();
  const theme = useTheme();
  const dark = theme.palette.mode === 'dark';
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { setMobileSidebarOpen } = useUIStore();
  const user = useAuthStore((s) => s.user);
  const title = usePageTitle();

  const { notifications, seed } = useNotificationStore();
  const unreadCount = notifications.filter((n) => !n.read).length;

  // Seed mock notifications once
  useEffect(() => {
    seed(SEED_NOTIFICATIONS);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Bell panel state
  const bellRef = useRef<HTMLDivElement>(null);
  const [bellAnchor, setBellAnchor] = useState<HTMLElement | null>(null);

  // Profile dialog state
  const [profileOpen, setProfileOpen] = useState(false);

  // Global search state
  const [searchOpen, setSearchOpen] = useState(false);

  // Ctrl+K / ⌘K shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <>
      <Box component="header" sx={{
        height: 52,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 3,
        bgcolor: dark ? 'rgba(23,33,51,0.92)' : 'rgba(255,255,255,0.88)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid',
        borderColor: 'divider',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        flexShrink: 0,
      }}>

        {/* Left: hamburger (mobile) + page title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 0 }}>
          {isMobile && (
            <Box
              onClick={() => setMobileSidebarOpen(true)}
              sx={{
                display: 'flex', p: '4px', borderRadius: '8px',
                color: dark ? '#94A3B8' : '#3E4850', cursor: 'pointer', flexShrink: 0,
                '&:hover': { color: '#00A8E8', bgcolor: dark ? 'rgba(255,255,255,0.06)' : '#F0F8FF' },
                transition: 'all 0.15s',
              }}
            >
              <HamburgerIcon />
            </Box>
          )}
          <Typography sx={{
            fontSize: 16, fontWeight: 600, color: 'text.primary',
            fontFamily: 'Inter, sans-serif', letterSpacing: '-0.01em',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {title}
          </Typography>
        </Box>

        {/* Center: search pill — opens GlobalSearchModal */}
        <Box
          onClick={() => setSearchOpen(true)}
          sx={{
            flex: 1, maxWidth: 400, mx: 3,
            display: { xs: 'none', md: 'flex' },
            alignItems: 'center', gap: 1,
            height: 32, px: 1.5,
            border: '1px solid',
            borderColor: dark ? 'rgba(255,255,255,0.12)' : '#E8EFF7',
            borderRadius: '999px',
            bgcolor: dark ? 'rgba(255,255,255,0.06)' : '#fff',
            color: dark ? '#94A3B8' : '#8FA3B8',
            cursor: 'pointer',
            boxShadow: dark ? 'none' : '0 1px 3px rgba(13,33,68,0.04)',
            '&:hover': { borderColor: '#00A8E8', color: '#00A8E8', bgcolor: dark ? 'rgba(0,168,232,0.08)' : 'rgba(0,168,232,0.02)' },
            transition: 'all 0.15s',
            userSelect: 'none',
          }}
        >
          <SearchIcon />
          <Typography sx={{ fontSize: 13, fontFamily: 'Inter, sans-serif', color: 'inherit', flex: 1 }}>
            {t('nav.search')}
          </Typography>
          <Box sx={{
            fontSize: 10, fontFamily: 'Inter, sans-serif', color: dark ? '#6B7A8D' : '#BDC8D1',
            border: '1px solid', borderColor: dark ? 'rgba(255,255,255,0.12)' : '#E8EFF7', borderRadius: '4px',
            px: '4px', py: '1px', fontWeight: 600,
          }}>
            ⌘K
          </Box>
        </Box>

        {/* Right cluster */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexShrink: 0 }}>

          {/* AI Active pill */}
          <Box sx={{
            display: { xs: 'none', sm: 'flex' }, alignItems: 'center', gap: 0.75,
            px: 1.25, py: '4px', borderRadius: '999px',
            bgcolor: 'rgba(0,168,232,0.08)',
            border: '1px solid rgba(0,168,232,0.2)',
          }}>
            <Box sx={{
              width: 7, height: 7, borderRadius: '50%', bgcolor: '#00A8E8',
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%,100%': { opacity: 1 }, '50%': { opacity: 0.4 },
              },
            }} />
            <Typography sx={{ fontSize: 10, fontWeight: 600, color: '#00A8E8', fontFamily: 'Inter, sans-serif', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              {t('nav.aiActive')}
            </Typography>
          </Box>

          {/* Language switcher */}
          <LangSwitcher />

          {/* Notification bell */}
          <Box
            ref={bellRef}
            onClick={() => setBellAnchor(bellRef.current)}
            sx={{
              position: 'relative', cursor: 'pointer',
              display: 'flex', p: '4px', borderRadius: '8px',
              bgcolor: bellAnchor ? (dark ? 'rgba(0,168,232,0.12)' : '#F0F8FF') : 'transparent',
              color: bellAnchor ? '#00A8E8' : (dark ? '#C8D6E5' : '#3E4850'),
              '&:hover': { color: '#00A8E8', bgcolor: dark ? 'rgba(0,168,232,0.12)' : '#F0F8FF' },
              transition: 'all 0.15s',
            }}
          >
            <BellIcon />
            {unreadCount > 0 && (
              <Box sx={{
                position: 'absolute', top: 2, right: 2,
                width: 14, height: 14, borderRadius: '50%',
                bgcolor: '#FF6B35', border: '1.5px solid #fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Typography sx={{ fontSize: 8, fontWeight: 700, color: '#fff', fontFamily: 'Inter, sans-serif', lineHeight: 1 }}>
                  {unreadCount > 9 ? '9+' : unreadCount}
                </Typography>
              </Box>
            )}
          </Box>

          {/* User avatar */}
          {user && (
            <Box
              onClick={() => setProfileOpen(true)}
              sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer',
                p: '3px', borderRadius: '8px',
                '&:hover': { bgcolor: dark ? 'rgba(255,255,255,0.06)' : '#F5F8FC' },
                transition: 'background 0.15s',
              }}
            >
              <Avatar firstName={user.first_name} lastName={user.last_name} />
              <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
                <Typography sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary', fontFamily: 'Inter, sans-serif', lineHeight: 1.2 }}>
                  {user.first_name}
                </Typography>
                <Typography sx={{ fontSize: 11, color: 'text.secondary', fontFamily: 'Inter, sans-serif', lineHeight: 1.2, textTransform: 'capitalize' }}>
                  {user.role.replace('_', ' ')}
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
      </Box>

      {/* Notification panel */}
      <NotificationPanel
        anchorEl={bellAnchor}
        onClose={() => setBellAnchor(null)}
      />

      {/* User profile dialog */}
      <UserProfileDialog
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
      />

      {/* Global search modal */}
      <GlobalSearchModal
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
      />
    </>
  );
}
