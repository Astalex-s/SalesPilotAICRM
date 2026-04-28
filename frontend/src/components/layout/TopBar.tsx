import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';

/* ── Inline language switcher for top bar ───────────────────────────────────── */
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

/* ── Route → page title map ─────────────────────────────────────────────────── */
function usePageTitle() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  if (pathname === '/')                    return t('nav.dashboard');
  if (pathname.startsWith('/leads/'))     return t('nav.leadDetail');
  if (pathname === '/leads')              return t('nav.leads');
  if (pathname === '/deals')              return t('nav.deals');
  if (pathname.startsWith('/pipeline/')) return t('nav.pipeline');
  if (pathname === '/users')              return t('nav.admin');
  return 'SalesPilotAI';
}

/* ── Notification bell with badge ───────────────────────────────────────────── */
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
  const initials = `${firstName[0] ?? ''}${lastName[0] ?? ''}`.toUpperCase();
  return (
    <Box sx={{
      width: 32, height: 32, borderRadius: '50%',
      bgcolor: '#0D2144', color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 12, fontWeight: 700, fontFamily: 'Inter, sans-serif',
      border: '1.5px solid #E8EFF7', flexShrink: 0,
    }}>
      {initials}
    </Box>
  );
}

/* ── TopBar ──────────────────────────────────────────────────────────────────── */
export default function TopBar() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const title = usePageTitle();

  return (
    <Box component="header" sx={{
      height: 52,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      px: 3,
      bgcolor: 'rgba(255,255,255,0.88)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid #E8EFF7',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      flexShrink: 0,
    }}>

      {/* Left: page title */}
      <Typography sx={{
        fontSize: 16, fontWeight: 600, color: '#191C1E',
        fontFamily: 'Inter, sans-serif', letterSpacing: '-0.01em',
        whiteSpace: 'nowrap',
      }}>
        {title}
      </Typography>

      {/* Center: search */}
      <Box sx={{
        flex: 1, maxWidth: 400, mx: 3,
        display: { xs: 'none', md: 'flex' },
        alignItems: 'center', gap: 1,
        height: 32, px: 1.5,
        border: '1px solid #E8EFF7',
        borderRadius: '999px',
        bgcolor: '#fff',
        color: '#8FA3B8',
        cursor: 'text',
        boxShadow: '0 1px 3px rgba(13,33,68,0.04)',
        '&:hover': { borderColor: '#BDC8D1' },
      }}>
        <SearchIcon />
        <Typography sx={{ fontSize: 13, fontFamily: 'Inter, sans-serif', color: '#8FA3B8', userSelect: 'none' }}>
          {t('nav.search')}
        </Typography>
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
        <Box sx={{
          position: 'relative', color: '#3E4850', cursor: 'pointer',
          display: 'flex', p: '4px', borderRadius: '8px',
          '&:hover': { color: '#00A8E8', bgcolor: '#F0F8FF' },
          transition: 'all 0.15s',
        }}>
          <BellIcon />
          <Box sx={{
            position: 'absolute', top: 2, right: 2,
            width: 14, height: 14, borderRadius: '50%',
            bgcolor: '#FF6B35', border: '1.5px solid #fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Typography sx={{ fontSize: 8, fontWeight: 700, color: '#fff', fontFamily: 'Inter, sans-serif', lineHeight: 1 }}>
              3
            </Typography>
          </Box>
        </Box>

        {/* User avatar */}
        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }}>
            <Avatar firstName={user.first_name} lastName={user.last_name} />
            <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
              <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#191C1E', fontFamily: 'Inter, sans-serif', lineHeight: 1.2 }}>
                {user.first_name}
              </Typography>
              <Typography sx={{ fontSize: 11, color: '#8FA3B8', fontFamily: 'Inter, sans-serif', lineHeight: 1.2, textTransform: 'capitalize' }}>
                {user.role.replace('_', ' ')}
              </Typography>
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
}
