import { Box, Typography } from '@mui/material';
import { Droppable } from 'react-beautiful-dnd';
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

export default function KanbanColumn({ stage, deals }: KanbanColumnProps) {
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
        }}
      >
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

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Deal count badge */}
          <Box
            sx={{
              px: 1,
              py: 0.2,
              borderRadius: '20px',
              bgcolor: 'rgba(13,33,68,0.08)',
              color: '#0D2144',
              fontFamily: 'Inter, sans-serif',
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            {deals.length}
          </Box>

          {/* Total value */}
          {valueLabel && (
            <Typography
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                fontWeight: 600,
                color: '#00A8E8',
              }}
            >
              {valueLabel}
            </Typography>
          )}
        </Box>
      </Box>

      {/* Droppable area */}
      <Droppable droppableId={stage.id}>
        {(provided, snapshot) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{
              flex: 1,
              minHeight: 120,
              borderRadius: '12px',
              bgcolor: snapshot.isDraggingOver
                ? 'rgba(0,168,232,0.06)'
                : '#F0F5FF',
              border: snapshot.isDraggingOver
                ? '2px dashed rgba(0,168,232,0.4)'
                : '2px dashed transparent',
              p: 1.25,
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

            {deals.length === 0 && !snapshot.isDraggingOver && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: 80,
                }}
              >
                <Typography
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12,
                    color: '#CBD5E8',
                  }}
                >
                  {t('pipeline.emptyColumn')}
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Droppable>
    </Box>
  );
}
