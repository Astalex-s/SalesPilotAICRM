import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import { Box, Typography } from '@mui/material';
import { Draggable } from 'react-beautiful-dnd';
import { useTranslation } from 'react-i18next';
import { type Deal } from '../../types/deal';

interface DealCardProps {
  deal: Deal;
  index: number;
  stageProbability: number;
}

/* ── Helpers ── */
const COMPANY_COLORS = ['#00A8E8', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#0D2144'];

function companyColor(name: string) {
  return COMPANY_COLORS[name.charCodeAt(0) % COMPANY_COLORS.length];
}

function companyInitials(name: string) {
  const words = name.trim().split(/\s+/);
  return words.length >= 2
    ? `${words[0][0]}${words[1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase();
}

function formatValue(amount: string, currency: string): string {
  const n = Number(amount);
  const sym = currency === 'USD' ? '$' : currency;
  if (n >= 1_000_000) return `${sym}${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${sym}${(n / 1_000).toFixed(0)}K`;
  return `${sym}${n.toFixed(0)}`;
}

function isOverdue(dateStr: string | null): boolean {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    day: '2-digit',
    month: 'short',
  });
}

const STATUS_LEFT_BORDER: Record<Deal['status'], string> = {
  open: 'transparent',
  won: '#10B981',
  lost: '#EF4444',
};

export default function DealCard({ deal, index, stageProbability }: DealCardProps) {
  const { t } = useTranslation();
  const isDraggable = deal.status === 'open';
  const overdue = isOverdue(deal.expected_close_date);
  const probPct = stageProbability <= 1
    ? Math.round(stageProbability * 100)
    : Math.round(stageProbability);

  const companyName = deal.company ?? deal.contact_name ?? '—';

  return (
    <Draggable draggableId={deal.id} index={index} isDragDisabled={!isDraggable}>
      {(provided, snapshot) => (
        <Box
          ref={provided.innerRef}
          {...provided.draggableProps}
          sx={{
            mb: 1.5,
            background: '#FFFFFF',
            border: '1px solid #E2EAF4',
            borderRadius: '12px',
            borderLeft: `3px solid ${STATUS_LEFT_BORDER[deal.status]}`,
            boxShadow: snapshot.isDragging
              ? '0 8px 32px rgba(13,33,68,0.14)'
              : '0 2px 8px rgba(13,33,68,0.06)',
            opacity: !isDraggable ? 0.65 : 1,
            transform: snapshot.isDragging ? 'scale(1.02)' : 'scale(1)',
            transition: 'box-shadow 0.15s ease, transform 0.12s ease',
            cursor: isDraggable ? (snapshot.isDragging ? 'grabbing' : 'grab') : 'not-allowed',
            position: 'relative',
            overflow: 'hidden',
            '&:hover .drag-handle': { opacity: 1 },
          }}
        >
          {/* Drag handle strip */}
          <Box
            {...provided.dragHandleProps}
            className="drag-handle"
            sx={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: 0,
              transition: 'opacity 0.15s',
              color: '#CBD5E8',
              cursor: 'grab',
            }}
          >
            <DragIndicatorIcon sx={{ fontSize: 14 }} />
          </Box>

          <Box sx={{ p: '12px 12px 12px 20px' }}>
            {/* Top row: company avatar + name */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              {deal.company ? (
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    borderRadius: '6px',
                    bgcolor: companyColor(deal.company),
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10,
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {companyInitials(deal.company)}
                </Box>
              ) : null}
              <Typography
                noWrap
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 12,
                  fontWeight: 600,
                  color: '#4B6080',
                  flex: 1,
                }}
              >
                {companyName}
              </Typography>
            </Box>

            {/* Deal title */}
            <Typography
              noWrap
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                fontWeight: 600,
                color: '#0D2144',
                mb: 1,
              }}
            >
              {deal.title}
            </Typography>

            {/* Value + probability */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 16,
                  fontWeight: 700,
                  color: '#00A8E8',
                }}
              >
                {formatValue(deal.value_amount, deal.value_currency)}
              </Typography>

              {probPct > 0 && (
                <Box
                  sx={{
                    px: 1,
                    py: 0.25,
                    borderRadius: '20px',
                    bgcolor: 'rgba(16,185,129,0.12)',
                    color: '#059669',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    fontWeight: 600,
                  }}
                >
                  {t('pipeline.likely', { prob: probPct })}
                </Box>
              )}
            </Box>

            {/* Footer: date */}
            {deal.expected_close_date && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <CalendarTodayIcon sx={{ fontSize: 11, color: overdue ? '#EF4444' : '#94A3B8' }} />
                <Typography
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    color: overdue ? '#EF4444' : '#94A3B8',
                    fontWeight: overdue ? 600 : 400,
                  }}
                >
                  {overdue
                    ? t('pipeline.overdue')
                    : formatDate(deal.expected_close_date)}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Draggable>
  );
}
