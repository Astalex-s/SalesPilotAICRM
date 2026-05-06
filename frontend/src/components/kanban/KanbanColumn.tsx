import { Box, Popover, Typography } from '@mui/material';
import { Droppable } from '@hello-pangea/dnd';
import { useRef, useState } from 'react';
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
  onAddDeal?: () => void;
  onAddLead?: () => void;
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
        height: 130,
        borderRadius: '12px',
        border: `2px dashed ${isDraggingOver ? 'rgba(0,168,232,0.5)' : '#D8E5F4'}`,
        bgcolor: isDraggingOver ? 'rgba(0,168,232,0.04)' : 'transparent',
        transition: 'all 0.15s ease',
        mb: 0,
      }}
    />
  );
}

/* ── Add card ghost button (with optional menu for lead/deal choice) ── */
function AddCardButton({
  onAddDeal,
  onAddLead,
}: {
  onAddDeal?: () => void;
  onAddLead?: () => void;
}) {
  const { t } = useTranslation();
  const anchorRef = useRef<HTMLDivElement | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  const hasMenu = !!(onAddDeal && onAddLead);

  const handleClick = () => {
    if (hasMenu) {
      setMenuOpen(true);
    } else if (onAddDeal) {
      onAddDeal();
    } else if (onAddLead) {
      onAddLead();
    }
  };

  const menuItems: { label: string; action: () => void }[] = [];
  if (onAddLead) menuItems.push({ label: t('pipeline.addLead'), action: () => { setMenuOpen(false); onAddLead(); } });
  if (onAddDeal) menuItems.push({ label: t('pipeline.addDeal'), action: () => { setMenuOpen(false); onAddDeal(); } });

  const isClickable = !!(onAddDeal || onAddLead);

  return (
    <>
      <Box
        ref={anchorRef}
        onClick={handleClick}
        sx={{
          mt: 1.5,
          height: 44,
          borderRadius: '12px',
          border: '1.5px dashed #D8E5F4',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: isClickable ? 'pointer' : 'default',
          transition: 'all 0.15s ease',
          '&:hover': isClickable ? {
            border: '1.5px dashed #00A8E8',
            bgcolor: 'rgba(0,168,232,0.04)',
            '& .add-icon': { color: '#00A8E8' },
          } : {},
        }}
      >
        <Box className="add-icon" sx={{ color: '#C4D4E8', display: 'flex', transition: 'color 0.15s' }}>
          <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </Box>
      </Box>

      {hasMenu && (
        <Popover
          open={menuOpen}
          anchorEl={anchorRef.current}
          onClose={() => setMenuOpen(false)}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          transformOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          PaperProps={{
            sx: {
              borderRadius: '10px',
              boxShadow: '0 4px 20px rgba(13,33,68,0.12)',
              border: '1px solid #E8EFF7',
              minWidth: 160,
              py: 0.5,
            },
          }}
        >
          {menuItems.map((item) => (
            <Box
              key={item.label}
              onClick={item.action}
              sx={{
                px: 2, py: 1,
                fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#0D2144',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 1,
                '&:hover': { bgcolor: 'rgba(0,168,232,0.06)', color: '#00A8E8' },
                transition: 'all 0.1s',
              }}
            >
              {item.label}
            </Box>
          ))}
        </Popover>
      )}
    </>
  );
}

export default function KanbanColumn({ stage, deals, onAddDeal, onAddLead }: KanbanColumnProps) {
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

      {/* Add card button — shows menu when both lead and deal actions available */}
      <AddCardButton onAddDeal={onAddDeal} onAddLead={onAddLead} />
    </Box>
  );
}
