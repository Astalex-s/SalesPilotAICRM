import { Box, Typography } from '@mui/material';
import { Droppable } from '@hello-pangea/dnd';
import { useTranslation } from 'react-i18next';
import { type Deal } from '../../types/deal';
import { type Stage } from '../../types/pipeline';
import DealCard from './DealCard';

/* ── Stage name i18n: map known stage names (any language) to i18n keys ── */
const STAGE_I18N_KEYS: Record<string, string> = {
  // Russian (seeded DB names)
  'квалификация':       'deals.stages.qualification',
  'предложение':        'deals.stages.proposal',
  'переговоры':         'deals.stages.negotiation',
  'закрыто: победа':    'deals.stages.closed_won',
  'закрыто: проигрыш':  'deals.stages.closed_lost',
  // English equivalents
  'qualification':      'deals.stages.qualification',
  'proposal':           'deals.stages.proposal',
  'negotiation':        'deals.stages.negotiation',
  'closed won':         'deals.stages.closed_won',
  'closed lost':        'deals.stages.closed_lost',
};

function translateStageName(name: string, t: (k: string) => string): string {
  const key = STAGE_I18N_KEYS[name.trim().toLowerCase()];
  return key ? t(key) : name;
}

interface KanbanColumnProps {
  stage: Stage;
  deals: Deal[];
}

function formatColumnValue(deals: Deal[]): string {
  const total = deals
    .filter((d) => d.status === 'open')
    .reduce((sum, d) => sum + Number(d.value_amount), 0);
  if (total === 0) return '';
  if (total >= 1_000_000) return `$${(total / 1_000_000).toFixed(1)}M`;
  if (total >= 1_000) return `$${(total / 1_000).toFixed(0)}K`;
  return `$${total}`;
}

/* ── Empty drop placeholder (card-sized dashed outline) ── */
function DropPlaceholder({ isDraggingOver }: { isDraggingOver: boolean }) {
  return (
    <Box
      sx={{
        height: 88,
        borderRadius: '12px',
        border: `2px dashed ${isDraggingOver ? 'rgba(0,168,232,0.5)' : '#D8E5F4'}`,
        bgcolor: isDraggingOver ? 'rgba(0,168,232,0.04)' : 'transparent',
        transition: 'all 0.15s ease',
        mb: 0,
      }}
    />
  );
}

/* ── Add deal ghost card ── */
function AddDealCard({ onClick }: { onClick?: () => void }) {
  return (
    <Box
      onClick={onClick}
      sx={{
        mt: 1.5,
        height: 44,
        borderRadius: '12px',
        border: '1.5px dashed #D8E5F4',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 0.75,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.15s ease',
        '&:hover': onClick ? {
          border: '1.5px dashed #00A8E8',
          bgcolor: 'rgba(0,168,232,0.04)',
          '& .add-icon': { color: '#00A8E8' },
          '& .add-label': { color: '#00A8E8' },
        } : {},
      }}
    >
      <Box
        className="add-icon"
        sx={{ color: '#C4D4E8', display: 'flex', transition: 'color 0.15s' }}
      >
        <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      </Box>
    </Box>
  );
}

export default function KanbanColumn({ stage, deals, onAddDeal }: KanbanColumnProps & { onAddDeal?: () => void }) {
  const { t } = useTranslation();
  const valueLabel = formatColumnValue(deals);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minWidth: 272,
        maxWidth: 272,
        flexShrink: 0,
      }}
    >
      {/* Column header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 1.5,
          px: 0.5,
          pb: 1,
          borderBottom: `3px solid ${stage.color ?? '#E8EFF7'}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          {stage.color && (
            <Box sx={{
              width: 10, height: 10, borderRadius: '50%',
              bgcolor: stage.color, flexShrink: 0,
            }} />
          )}
          <Typography
            sx={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 700,
              fontSize: 14,
              color: '#0D2144',
            }}
          >
            {translateStageName(stage.name, t)}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              px: 1, py: 0.2, borderRadius: '20px',
              bgcolor: 'rgba(13,33,68,0.08)', color: '#0D2144',
              fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 700,
            }}
          >
            {deals.length}
          </Box>
          {valueLabel && (
            <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 600, color: '#00A8E8' }}>
              {valueLabel}
            </Typography>
          )}
        </Box>
      </Box>

      {/* Droppable area — no background, cards float freely */}
      <Droppable droppableId={stage.id}>
        {(provided, snapshot) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{
              flex: 1,
              transition: 'all 0.15s ease',
            }}
          >
            {deals.map((deal, index) => (
              <DealCard
                key={deal.id}
                deal={deal}
                index={index}
                stageProbability={stage.probability}
              />
            ))}
            {provided.placeholder}

            {/* Empty drop target — shown when column has no cards */}
            {deals.length === 0 && (
              <DropPlaceholder isDraggingOver={snapshot.isDraggingOver} />
            )}
          </Box>
        )}
      </Droppable>

      {/* Add deal ghost card — always visible below cards */}
      <AddDealCard onClick={onAddDeal} />
    </Box>
  );
}
