import { Box, Menu, MenuItem, Tooltip, Typography, useTheme } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { useKanbanStore } from '../../store/useKanbanStore';
import { useUIStore } from '../../store/useUIStore';

/* ── Icon components (inline SVG — no extra dep) ────────────────────────────── */
const Icon = ({ d, size = 20 }: { d: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

const ICONS = {
  dashboard:   'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10',
  leads:       'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M9 11a4 4 0 100-8 4 4 0 000 8z M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75',
  deals:       'M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z M7 7h.01',
  pipeline:    'M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z',
  gmail:       'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6',
  telegram:    'M22 2L11 13 M22 2L15 22l-4-9-9-4 22-9z',
  ai:          'M12 2a2 2 0 012 2v1a7 7 0 010 14v1a2 2 0 01-4 0v-1a7 7 0 010-14V4a2 2 0 012-2z M8 12h.01 M12 12h.01 M16 12h.01',
  analytics:   'M18 20V10 M12 20V4 M6 20v-6',
  admin:       'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
  gdpr:        'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z M9 12l2 2 4-4',
  settings:    'M12 15a3 3 0 100-6 3 3 0 000 6z M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z',
  logout:      'M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4 M16 17l5-5-5-5 M21 12H9',
  menu:        'M3 12h18 M3 6h18 M3 18h18',
};

/* ── Theme-aware colour tokens (computed inside components via hook) ─────────── */
function useSidebarColors() {
  const theme = useTheme();
  const dark = theme.palette.mode === 'dark';
  return {
    bg:          theme.palette.background.paper,
    border:      theme.palette.divider,
    active:      dark ? 'rgba(0,168,232,0.15)' : '#F0F8FF',
    activeLine:  '#00A8E8',
    activeText:  '#00A8E8',
    hoverBg:     dark ? 'rgba(255,255,255,0.06)' : '#F5F8FC',
    iconDefault: dark ? '#94A3B8' : '#3E4850',
    sectionCap:  theme.palette.text.secondary,
    text:        theme.palette.text.primary,
  };
}

/* ── Single nav item ─────────────────────────────────────────────────────────── */
interface NavItemProps {
  iconPath: string;
  label: string;
  active: boolean;
  onClick: () => void;
  expanded: boolean;
  badge?: React.ReactNode;
  cyan?: boolean;
}

function NavItem({ iconPath, label, active, onClick, expanded, badge, cyan }: NavItemProps) {
  const C = useSidebarColors();
  const color = cyan ? C.activeLine : active ? C.activeText : C.iconDefault;

  const inner = (
    <Box
      onClick={onClick}
      sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: expanded ? 1.5 : 0,
        justifyContent: expanded ? 'flex-start' : 'center',
        px: expanded ? '12px' : 0,
        py: '8px',
        mx: expanded ? '8px' : 'auto',
        width: expanded ? 'calc(100% - 16px)' : 40,
        height: 40,
        borderRadius: '8px',
        bgcolor: active ? C.active : 'transparent',
        color,
        cursor: 'pointer',
        transition: 'background 0.15s, color 0.15s',
        '&:hover': { bgcolor: active ? C.active : C.hoverBg },
      }}
    >
      {/* Active indicator */}
      {active && (
        <Box sx={{
          position: 'absolute', left: expanded ? -8 : -8,
          top: '50%', transform: 'translateY(-50%)',
          width: 3, height: 20, bgcolor: C.activeLine,
          borderRadius: '0 2px 2px 0',
        }} />
      )}
      <Box sx={{ color, flexShrink: 0, display: 'flex' }}>
        <Icon d={iconPath} />
      </Box>
      {expanded && (
        <Typography sx={{
          fontSize: 13, fontWeight: active || cyan ? 600 : 400,
          fontFamily: 'Inter, sans-serif', color, lineHeight: 1,
        }}>
          {label}
        </Typography>
      )}
      {badge}
    </Box>
  );

  return expanded ? inner : (
    <Tooltip title={label} placement="right" arrow>
      {inner}
    </Tooltip>
  );
}

/* ── Section label (expanded only) ──────────────────────────────────────────── */
function SectionLabel({ label }: { label: string }) {
  const C = useSidebarColors();
  return (
    <Typography sx={{
      fontSize: 11, fontWeight: 600, letterSpacing: '0.06em',
      fontFamily: 'Inter, sans-serif', color: C.sectionCap,
      textTransform: 'uppercase', px: '20px', pt: 2, pb: 0.5,
    }}>
      {label}
    </Typography>
  );
}

/* ── Pulsing dot badge ───────────────────────────────────────────────────────── */
const PulsingDot = () => (
  <Box sx={{
    width: 7, height: 7, borderRadius: '50%',
    bgcolor: '#00A8E8', ml: 'auto', flexShrink: 0,
    animation: 'pulse 2s ease-in-out infinite',
    '@keyframes pulse': {
      '0%, 100%': { opacity: 1, transform: 'scale(1)' },
      '50%':       { opacity: 0.5, transform: 'scale(0.85)' },
    },
  }} />
);

/* ── Pipeline nav item with pipeline switcher flyout ────────────────────────── */
function PipelineNavItem({ expanded }: { expanded: boolean }) {
  const C = useSidebarColors();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { allPipelines, loadPipelines } = useKanbanStore();
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const itemRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadPipelines(); }, [loadPipelines]);

  const isActive = pathname.startsWith('/pipeline/');
  const activePipelineId = isActive ? pathname.split('/pipeline/')[1] : null;

  const handleClick = (e: React.MouseEvent<HTMLElement>) => {
    if (allPipelines.length <= 1) {
      const id = allPipelines[0]?.id ?? '00000000-0000-0000-0000-000000000001';
      navigate(`/pipeline/${id}`);
    } else {
      setAnchorEl(e.currentTarget);
    }
  };

  const handleSelect = (id: string) => {
    setAnchorEl(null);
    navigate(`/pipeline/${id}`);
  };

  const color = isActive ? C.activeText : C.iconDefault;

  const inner = (
    <Box
      ref={itemRef}
      onClick={handleClick}
      sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: expanded ? 1.5 : 0,
        justifyContent: expanded ? 'flex-start' : 'center',
        px: expanded ? '12px' : 0,
        py: '8px',
        mx: expanded ? '8px' : 'auto',
        width: expanded ? 'calc(100% - 16px)' : 40,
        height: 40,
        borderRadius: '8px',
        bgcolor: isActive ? C.active : 'transparent',
        color,
        cursor: 'pointer',
        transition: 'background 0.15s, color 0.15s',
        '&:hover': { bgcolor: isActive ? C.active : C.hoverBg },
      }}
    >
      {isActive && (
        <Box sx={{
          position: 'absolute', left: -8, top: '50%', transform: 'translateY(-50%)',
          width: 3, height: 20, bgcolor: C.activeLine, borderRadius: '0 2px 2px 0',
        }} />
      )}
      <Box sx={{ color, flexShrink: 0, display: 'flex' }}>
        <Icon d={ICONS.pipeline} />
      </Box>
      {expanded && (
        <>
          <Typography sx={{
            fontSize: 13, fontWeight: isActive ? 600 : 400,
            fontFamily: 'Inter, sans-serif', color, lineHeight: 1, flex: 1,
          }}>
            {t('nav.pipeline')}
          </Typography>
          {allPipelines.length > 1 && (
            <Box sx={{ color: C.sectionCap, display: 'flex', ml: 'auto' }}>
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </Box>
          )}
        </>
      )}
    </Box>
  );

  return (
    <>
      {expanded ? inner : (
        <Tooltip title={t('nav.pipeline')} placement="right" arrow>
          {inner}
        </Tooltip>
      )}

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{
          sx: {
            borderRadius: '10px',
            boxShadow: '0 4px 20px rgba(13,33,68,0.12)',
            border: `1px solid`,
            borderColor: 'divider',
            minWidth: 200,
            ml: 0.5,
          },
        }}
      >
        <Typography sx={{
          px: 2, pt: 1.25, pb: 0.5,
          fontSize: 10, fontWeight: 600, letterSpacing: '0.07em',
          textTransform: 'uppercase', color: '#94A3B8', fontFamily: 'Inter, sans-serif',
        }}>
          {t('nav.pipeline')}
        </Typography>
        {allPipelines.map((p) => (
          <MenuItem
            key={p.id}
            onClick={() => handleSelect(p.id)}
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              fontWeight: activePipelineId === p.id ? 600 : 400,
              color: activePipelineId === p.id ? C.activeLine : C.text,
              borderRadius: '6px',
              mx: 0.75,
              my: 0.25,
              px: 1.5,
              '&:hover': { bgcolor: C.hoverBg },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
              {activePipelineId === p.id && (
                <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: C.activeLine, flexShrink: 0 }} />
              )}
              {activePipelineId !== p.id && (
                <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#E2EAF4', flexShrink: 0 }} />
              )}
              <Typography noWrap sx={{ fontFamily: 'inherit', fontSize: 'inherit', fontWeight: 'inherit', color: 'inherit' }}>
                {p.name}
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}

/* ── Avatar initials ─────────────────────────────────────────────────────────── */
function UserAvatar({ firstName, lastName, size = 32 }: { firstName: string; lastName: string; size?: number }) {
  const initials = `${firstName[0] ?? ''}${lastName[0] ?? ''}`.toUpperCase();
  return (
    <Box sx={{
      width: size, height: size, borderRadius: '50%',
      bgcolor: '#00A8E8', color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.38, fontWeight: 700, fontFamily: 'Inter, sans-serif',
      flexShrink: 0,
    }}>
      {initials}
    </Box>
  );
}

/* ── Main Sidebar ────────────────────────────────────────────────────────────── */
export default function Sidebar({
  forceExpanded = false,
  inDrawer = false,
}: {
  forceExpanded?: boolean;
  inDrawer?: boolean;
}) {
  const C = useSidebarColors();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const { sidebarOpen, toggleSidebar } = useUIStore();

  const expanded = forceExpanded || sidebarOpen;
  const W = expanded ? 220 : 64;

  const isActive = (path: string) =>
    path === '/' ? pathname === '/' : pathname.startsWith(path);

  const go = (path: string) => navigate(path);

  const handleLogout = () => { logout(); navigate('/login', { replace: true }); };

  /* ── Nav sections ── */
  type NavEntry = {
    iconKey: keyof typeof ICONS;
    labelKey: string;
    path: string;
    cyan?: boolean;
    badge?: React.ReactNode;
    adminOnly?: boolean;
  };

  const sections: { sectionKey: string; items: NavEntry[] }[] = [
    {
      sectionKey: 'nav.sections.sales',
      items: [
        { iconKey: 'dashboard', labelKey: 'nav.dashboard', path: '/' },
        { iconKey: 'leads',     labelKey: 'nav.leads',     path: '/leads' },
        { iconKey: 'deals',     labelKey: 'nav.deals',     path: '/deals' },
      ],
    },
    {
      sectionKey: 'nav.sections.communication',
      items: [
        { iconKey: 'gmail',    labelKey: 'nav.gmail',    path: '/gmail' },
        { iconKey: 'telegram', labelKey: 'nav.telegram', path: '/telegram' },
      ],
    },
    {
      sectionKey: 'nav.sections.intelligence',
      items: [
        { iconKey: 'ai', labelKey: 'nav.aiAssistant', path: '/ai-assistant', cyan: true, badge: <PulsingDot /> },
      ],
    },
    {
      sectionKey: 'nav.sections.system',
      items: [
        { iconKey: 'analytics', labelKey: 'nav.analytics', path: '/analytics' },
        { iconKey: 'admin',     labelKey: 'nav.admin',     path: '/users',  adminOnly: true },
        { iconKey: 'gdpr',      labelKey: 'nav.gdpr',      path: '/gdpr',   adminOnly: true },
      ],
    },
  ];

  return (
    <Box sx={{
      width: W,
      minWidth: W,
      height: inDrawer ? '100%' : '100vh',
      bgcolor: C.bg,
      borderRight: inDrawer ? 'none' : `1px solid ${C.border}`,
      display: 'flex',
      flexDirection: 'column',
      transition: 'width 0.22s ease, min-width 0.22s ease',
      overflow: 'hidden',
      flexShrink: 0,
      ...(inDrawer ? {} : { position: 'sticky', top: 0, zIndex: 100 }),
    }}>

      {/* Logo / toggle */}
      <Box sx={{
        height: 64, display: 'flex', alignItems: 'center',
        px: expanded ? 2 : 0, justifyContent: expanded ? 'space-between' : 'center',
        borderBottom: `1px solid ${C.border}`,
        flexShrink: 0,
      }}>
        {expanded ? (
          <>
            <Box component="img" src="/logo.png" alt="SalesPilotAI" sx={{ height: 36, display: 'block' }} />
            <Box
              onClick={toggleSidebar}
              sx={{ color: C.iconDefault, cursor: 'pointer', display: 'flex', '&:hover': { color: C.activeLine } }}
            >
              <Icon d={ICONS.menu} />
            </Box>
          </>
        ) : (
          <Tooltip title="Expand sidebar" placement="right" arrow>
            <Box onClick={toggleSidebar} sx={{ cursor: 'pointer', color: C.activeLine, display: 'flex' }}>
              <Icon d={ICONS.menu} />
            </Box>
          </Tooltip>
        )}
      </Box>

      {/* Nav sections */}
      <Box sx={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', py: 1 }}>
        {sections.map(({ sectionKey, items }) => {
          const visibleItems = items.filter(
            (item) => !item.adminOnly || user?.role === 'admin'
          );
          if (!visibleItems.length) return null;

          return (
            <Box key={sectionKey}>
              {expanded && <SectionLabel label={t(sectionKey)} />}
              {!expanded && <Box sx={{ height: 8 }} />}
              {visibleItems.map((item) => (
                <NavItem
                  key={item.path}
                  iconPath={ICONS[item.iconKey]}
                  label={t(item.labelKey)}
                  active={isActive(item.path)}
                  onClick={() => item.path.startsWith('#') ? undefined : go(item.path)}
                  expanded={expanded}
                  badge={item.badge}
                  cyan={item.cyan}
                />
              ))}
              {sectionKey === 'nav.sections.sales' && (
                <PipelineNavItem expanded={expanded} />
              )}
            </Box>
          );
        })}
      </Box>

      {/* Bottom: user + settings + logout */}
      <Box sx={{
        borderTop: `1px solid ${C.border}`,
        p: expanded ? '12px 16px' : '12px 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: expanded ? 'space-between' : 'center',
        flexShrink: 0,
        gap: 1,
      }}>
        {user && (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 0 }}>
              <UserAvatar firstName={user.first_name} lastName={user.last_name} />
              {expanded && (
                <Box sx={{ minWidth: 0 }}>
                  <Typography sx={{ fontSize: 13, fontWeight: 600, color: C.text, fontFamily: 'Inter, sans-serif', lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {user.first_name} {user.last_name}
                  </Typography>
                  <Typography sx={{ fontSize: 11, color: C.sectionCap, fontFamily: 'Inter, sans-serif', lineHeight: 1.2, textTransform: 'capitalize' }}>
                    {user.role.replace('_', ' ')}
                  </Typography>
                </Box>
              )}
            </Box>
            {expanded && (
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Tooltip title={t('nav.settings')} arrow>
                  <Box onClick={() => go('/settings')} sx={{ color: C.sectionCap, cursor: 'pointer', display: 'flex', p: '4px', borderRadius: '6px', '&:hover': { color: C.activeText, bgcolor: C.hoverBg } }}>
                    <Icon d={ICONS.settings} size={18} />
                  </Box>
                </Tooltip>
                <Tooltip title={t('nav.logout')} arrow>
                  <Box onClick={handleLogout} sx={{ color: C.sectionCap, cursor: 'pointer', display: 'flex', p: '4px', borderRadius: '6px', '&:hover': { color: '#EF4444', bgcolor: '#FFF5F5' } }}>
                    <Icon d={ICONS.logout} size={18} />
                  </Box>
                </Tooltip>
              </Box>
            )}
            {!expanded && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Tooltip title={t('nav.settings')} placement="right" arrow>
                  <Box onClick={() => go('/settings')} sx={{ color: C.sectionCap, cursor: 'pointer', display: 'flex', p: '4px', borderRadius: '6px', '&:hover': { color: C.activeText, bgcolor: C.hoverBg } }}>
                    <Icon d={ICONS.settings} size={18} />
                  </Box>
                </Tooltip>
                <Tooltip title={t('nav.logout')} placement="right" arrow>
                  <Box onClick={handleLogout} sx={{ color: C.sectionCap, cursor: 'pointer', display: 'flex', p: '4px', borderRadius: '6px', '&:hover': { color: '#EF4444', bgcolor: '#FFF5F5' } }}>
                    <Icon d={ICONS.logout} size={18} />
                  </Box>
                </Tooltip>
              </Box>
            )}
          </>
        )}
      </Box>
    </Box>
  );
}
