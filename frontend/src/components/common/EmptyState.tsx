/**
 * EmptyState — reusable illustrated placeholder for empty lists/tables.
 *
 * Usage inside a table:
 *   <TableCell colSpan={N} sx={{ border: 'none' }}>
 *     <EmptyState icon="leads" title={t('leads.noLeads')} subtitle={t('leads.noLeadsSubtitle')} />
 *   </TableCell>
 *
 * Usage standalone:
 *   <EmptyState icon="activity" title={t('leadDetail.timeline.empty')} />
 */
import { Box, Button, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import type { SxProps } from '@mui/material/styles';

// ── Illustration types ────────────────────────────────────────────────────────

export type EmptyStateIcon =
  | 'leads'
  | 'deals'
  | 'mail'
  | 'activity'
  | 'users'
  | 'shield'
  | 'search';

interface Illustration {
  color: string;
  bg: string;
  paths: React.ReactNode;
}

const ILLUSTRATIONS: Record<EmptyStateIcon, Illustration> = {
  leads: {
    color: '#00A8E8',
    bg: 'rgba(0,168,232,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#00A8E8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
      </svg>
    ),
  },
  deals: {
    color: '#FF6B35',
    bg: 'rgba(255,107,53,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#FF6B35" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" />
        <line x1="7" y1="7" x2="7.01" y2="7" strokeWidth="2.5" />
      </svg>
    ),
  },
  mail: {
    color: '#8B5CF6',
    bg: 'rgba(139,92,246,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#8B5CF6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
        <polyline points="22,6 12,13 2,6" />
      </svg>
    ),
  },
  activity: {
    color: '#F59E0B',
    bg: 'rgba(245,158,11,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  users: {
    color: '#0D2144',
    bg: 'rgba(13,33,68,0.06)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#0D2144" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
        <circle cx="9" cy="7" r="4" />
      </svg>
    ),
  },
  shield: {
    color: '#10B981',
    bg: 'rgba(16,185,129,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#10B981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <polyline points="9 12 11 14 15 10" />
      </svg>
    ),
  },
  search: {
    color: '#64748B',
    bg: 'rgba(100,116,139,0.08)',
    paths: (
      <svg width={40} height={40} viewBox="0 0 24 24" fill="none"
        stroke="#64748B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
        <line x1="8" y1="11" x2="14" y2="11" />
        <line x1="11" y1="8" x2="11" y2="14" />
      </svg>
    ),
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon: EmptyStateIcon;
  title: string;
  subtitle?: string;
  action?: { label: string; onClick: () => void };
  compact?: boolean;
  sx?: SxProps;
}

export default function EmptyState({
  icon,
  title,
  subtitle,
  action,
  compact = false,
  sx,
}: EmptyStateProps) {
  const theme = useTheme();
  const dark = theme.palette.mode === 'dark';
  const illus = ILLUSTRATIONS[icon];

  // In dark mode, lighten the icon colour slightly and keep bg subtle
  const bgColor = dark
    ? illus.bg.replace('0.08', '0.12').replace('0.06', '0.10')
    : illus.bg;

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      py: compact ? 5 : 8,
      px: 2,
      gap: 1.5,
      ...sx,
    }}>
      {/* Illustration circle */}
      <Box sx={{
        width: 80,
        height: 80,
        borderRadius: '50%',
        bgcolor: bgColor,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mb: 0.5,
        flexShrink: 0,
      }}>
        {illus.paths}
      </Box>

      {/* Title */}
      <Typography sx={{
        fontSize: 15,
        fontWeight: 600,
        color: 'text.primary',
        fontFamily: 'Inter, sans-serif',
        textAlign: 'center',
        lineHeight: 1.3,
      }}>
        {title}
      </Typography>

      {/* Subtitle */}
      {subtitle && (
        <Typography sx={{
          fontSize: 13,
          color: 'text.secondary',
          fontFamily: 'Inter, sans-serif',
          textAlign: 'center',
          maxWidth: 300,
          lineHeight: 1.6,
        }}>
          {subtitle}
        </Typography>
      )}

      {/* CTA button */}
      {action && (
        <Button
          onClick={action.onClick}
          variant="contained"
          size="small"
          disableElevation
          sx={{
            mt: 0.5,
            bgcolor: illus.color,
            color: '#fff',
            '&:hover': { bgcolor: illus.color, filter: 'brightness(0.9)' },
            borderRadius: '8px',
            textTransform: 'none',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 13,
            px: 2,
          }}
        >
          {action.label}
        </Button>
      )}
    </Box>
  );
}
