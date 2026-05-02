import { Box, Typography } from '@mui/material';
import { Draggable } from '@hello-pangea/dnd';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { type Lead, type LeadStatus } from '../../types/lead';

const STATUS_COLORS: Record<LeadStatus, { bg: string; text: string }> = {
  new:         { bg: 'rgba(0,168,232,0.1)',    text: '#00A8E8' },
  contacted:   { bg: 'rgba(245,158,11,0.1)',   text: '#D97706' },
  qualified:   { bg: 'rgba(16,185,129,0.1)',   text: '#059669' },
  unqualified: { bg: 'rgba(148,163,184,0.15)', text: '#94A3B8' },
  converted:   { bg: 'rgba(139,92,246,0.1)',   text: '#7C3AED' },
};

interface LeadCardProps {
  lead: Lead;
  index: number;
}

export default function LeadCard({ lead, index }: LeadCardProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const statusStyle = STATUS_COLORS[lead.status];
  const displayName = `${lead.first_name} ${lead.last_name}`;
  const initials = `${lead.first_name[0] ?? ''}${lead.last_name[0] ?? ''}`.toUpperCase();

  return (
    <Draggable draggableId={`lead-${lead.id}`} index={index}>
      {(provided, snapshot) => (
        <Box
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          sx={{
            mb: 1.5,
            background: '#FFFFFF',
            border: '1px solid #E2EAF4',
            borderLeft: '3px solid #00A8E8',
            borderRadius: '12px',
            boxShadow: snapshot.isDragging
              ? '0 8px 32px rgba(13,33,68,0.14)'
              : '0 2px 8px rgba(13,33,68,0.06)',
            transition: 'box-shadow 0.15s ease',
            cursor: snapshot.isDragging ? 'grabbing' : 'grab',
            position: 'relative',
            '&:hover .lead-nav-btn': { opacity: 1 },
          }}
        >
          <Box sx={{ p: '10px 12px' }}>
            {/* Top row: avatar + name + navigate */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.75 }}>
              <Box sx={{
                width: 28, height: 28, borderRadius: '6px',
                bgcolor: '#E8EFF7', color: '#4B6080',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 700,
                flexShrink: 0,
              }}>
                {initials}
              </Box>
              <Typography noWrap sx={{
                fontFamily: 'Inter, sans-serif', fontSize: 13,
                fontWeight: 600, color: '#0D2144', flex: 1,
              }}>
                {displayName}
              </Typography>
              <Box
                className="lead-nav-btn"
                onClick={(e) => { e.stopPropagation(); navigate(`/leads/${lead.id}`); }}
                sx={{
                  opacity: 0, cursor: 'pointer', color: '#94A3B8',
                  display: 'flex', flexShrink: 0,
                  transition: 'opacity 0.15s, color 0.15s',
                  '&:hover': { color: '#00A8E8' },
                }}
              >
                <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </Box>
            </Box>

            {/* Company or email */}
            <Typography noWrap sx={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, color: '#64748B', mb: 0.75,
            }}>
              {lead.company ?? lead.email}
            </Typography>

            {/* Status badge */}
            <Box sx={{
              display: 'inline-flex', alignItems: 'center',
              px: 0.75, py: 0.15, borderRadius: '6px',
              bgcolor: statusStyle.bg, color: statusStyle.text,
              fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 700,
            }}>
              {t(`leads.status.${lead.status}`)}
            </Box>
          </Box>
        </Box>
      )}
    </Draggable>
  );
}
