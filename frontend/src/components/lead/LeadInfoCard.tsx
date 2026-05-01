import BusinessIcon from '@mui/icons-material/Business';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import SourceIcon from '@mui/icons-material/Source';
import { Box, Card, CircularProgress, Divider, Menu, MenuItem, Tooltip, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { type Lead, type LeadStatus } from '../../types/lead';

/* ── Status badge ── */
const STATUS_STYLE: Record<LeadStatus, { bg: string; color: string }> = {
  new:         { bg: 'rgba(0,168,232,0.12)',  color: '#0090CC' },
  contacted:   { bg: 'rgba(245,158,11,0.12)', color: '#D97706' },
  qualified:   { bg: 'rgba(16,185,129,0.12)', color: '#059669' },
  unqualified: { bg: 'rgba(239,68,68,0.12)',  color: '#DC2626' },
  converted:   { bg: 'rgba(13,33,68,0.10)',   color: '#0D2144' },
};

/* ── Avatar helpers ── */
function avatarInitials(lead: Lead) {
  return `${lead.first_name[0] ?? ''}${lead.last_name[0] ?? ''}`.toUpperCase();
}

/* ── Contact row ── */
function ContactRow({
  icon,
  value,
}: {
  icon: React.ReactNode;
  value: string | null | undefined;
}) {
  if (!value) return null;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, py: 0.75 }}>
      <Box sx={{ color: '#94A3B8', display: 'flex', flexShrink: 0 }}>{icon}</Box>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 13,
          color: '#4B6080',
          wordBreak: 'break-all',
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}

/* ── Meta row ── */
function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 11,
          fontWeight: 500,
          letterSpacing: '0.07em',
          textTransform: 'uppercase',
          color: '#94A3B8',
          mb: 0.25,
        }}
      >
        {label}
      </Typography>
      <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#4B6080' }}>
        {value}
      </Typography>
    </Box>
  );
}

// Valid status transitions (mirrors domain state machine)
const VALID_TRANSITIONS: Record<LeadStatus, LeadStatus[]> = {
  new:         ['contacted', 'qualified', 'unqualified'],
  contacted:   ['qualified', 'unqualified'],
  qualified:   ['unqualified'],
  unqualified: ['qualified', 'contacted'],
  converted:   [],
};

interface LeadInfoCardProps {
  lead: Lead;
  onStatusChange?: (newStatus: LeadStatus) => Promise<void>;
}

export default function LeadInfoCard({ lead, onStatusChange }: LeadInfoCardProps) {
  const { t } = useTranslation();
  const s = STATUS_STYLE[lead.status];

  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  const validNext = VALID_TRANSITIONS[lead.status];
  const canChange = validNext.length > 0 && !!onStatusChange;

  const handleBadgeClick = (e: React.MouseEvent<HTMLElement>) => {
    if (!canChange) return;
    setStatusError(null);
    setAnchorEl(e.currentTarget);
  };

  const handleStatusSelect = async (newStatus: LeadStatus) => {
    setAnchorEl(null);
    if (!onStatusChange) return;
    setStatusLoading(true);
    setStatusError(null);
    try {
      await onStatusChange(newStatus);
    } catch (err) {
      setStatusError(err instanceof Error ? err.message : 'Status update failed');
    } finally {
      setStatusLoading(false);
    }
  };

  return (
    <Card
      elevation={0}
      sx={{
        background: '#FFFFFF',
        border: '1px solid #E2EAF4',
        borderRadius: '16px',
        boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
      }}
    >
      <Box sx={{ p: 2.5 }}>
        {/* Avatar + name */}
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2.5 }}>
          <Box
            sx={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #0D2144 0%, #162E5C 100%)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'Inter, sans-serif',
              fontSize: 24,
              fontWeight: 700,
              mb: 1.5,
              flexShrink: 0,
            }}
          >
            {avatarInitials(lead)}
          </Box>

          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 700,
              fontSize: 17,
              color: '#0D2144',
              textAlign: 'center',
              lineHeight: 1.3,
            }}
          >
            {lead.first_name} {lead.last_name}
          </Typography>

          {lead.company && (
            <Typography
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                color: '#94A3B8',
                mt: 0.25,
                textAlign: 'center',
              }}
            >
              {lead.company}
            </Typography>
          )}

          {/* Status badge — clickable when transitions are available */}
          <Tooltip title={canChange ? t('leads.changeStatus') : ''} placement="top">
            <Box
              onClick={handleBadgeClick}
              sx={{
                mt: 1.25,
                px: 1.5,
                py: 0.4,
                borderRadius: '20px',
                bgcolor: s.bg,
                color: s.color,
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                cursor: canChange ? 'pointer' : 'default',
                userSelect: 'none',
                transition: 'opacity 0.15s',
                '&:hover': canChange ? { opacity: 0.8 } : {},
              }}
            >
              {statusLoading
                ? <CircularProgress size={12} sx={{ color: s.color }} />
                : t(`leads.status.${lead.status}`)
              }
              {canChange && !statusLoading && (
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              )}
            </Box>
          </Tooltip>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            PaperProps={{ sx: { borderRadius: '10px', boxShadow: '0 4px 20px rgba(13,33,68,0.12)', minWidth: 160 } }}
          >
            {validNext.map((status) => {
              const st = STATUS_STYLE[status];
              return (
                <MenuItem
                  key={status}
                  onClick={() => handleStatusSelect(status)}
                  sx={{ fontFamily: 'Inter', fontSize: 13, gap: 1 }}
                >
                  <Box sx={{
                    px: 1, py: 0.2, borderRadius: '12px',
                    bgcolor: st.bg, color: st.color,
                    fontSize: 12, fontWeight: 600,
                  }}>
                    {t(`leads.status.${status}`)}
                  </Box>
                </MenuItem>
              );
            })}
          </Menu>

          {statusError && (
            <Typography sx={{
              mt: 0.75, fontSize: 11, color: '#DC2626',
              fontFamily: 'Inter, sans-serif', textAlign: 'center',
              maxWidth: 200,
            }}>
              {statusError}
            </Typography>
          )}
        </Box>

        <Divider sx={{ borderColor: '#F0F5FF', mb: 2 }} />

        {/* Contact info */}
        <Box sx={{ mb: 2 }}>
          <ContactRow icon={<EmailIcon sx={{ fontSize: 16 }} />} value={lead.email} />
          <ContactRow icon={<PhoneIcon sx={{ fontSize: 16 }} />} value={lead.phone} />
          <ContactRow icon={<BusinessIcon sx={{ fontSize: 16 }} />} value={lead.company} />
          <ContactRow
            icon={<SourceIcon sx={{ fontSize: 16 }} />}
            value={t(`leads.source.${lead.source}`, lead.source)}
          />
        </Box>

        {lead.notes && (
          <>
            <Divider sx={{ borderColor: '#F0F5FF', mb: 1.5 }} />
            <Typography
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
                fontWeight: 500,
                letterSpacing: '0.07em',
                textTransform: 'uppercase',
                color: '#94A3B8',
                mb: 0.5,
              }}
            >
              {t('leadDetail.info.notes')}
            </Typography>
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#4B6080' }}>
              {lead.notes}
            </Typography>
          </>
        )}

        <Divider sx={{ borderColor: '#F0F5FF', my: 2 }} />

        {/* Meta */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <MetaRow
            label={t('leadDetail.info.created')}
            value={new Date(lead.created_at).toLocaleDateString(undefined, {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })}
          />
          <MetaRow
            label={t('leadDetail.info.updated')}
            value={new Date(lead.updated_at).toLocaleDateString(undefined, {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })}
          />
        </Box>
      </Box>
    </Card>
  );
}
