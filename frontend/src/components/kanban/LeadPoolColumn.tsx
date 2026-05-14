import { Box, Typography } from '@mui/material';
import { Droppable } from '@hello-pangea/dnd';
import { useTranslation } from 'react-i18next';
import { type Lead } from '../../types/lead';
import LeadCard from './LeadCard';

export const LEADS_POOL_ID = 'leads-pool';

function DropPlaceholder({ isDraggingOver }: { isDraggingOver: boolean }) {
  return (
    <Box
      sx={{
        height: 130,
        borderRadius: '12px',
        border: `2px dashed ${isDraggingOver ? 'rgba(0,168,232,0.5)' : '#D8E5F4'}`,
        bgcolor: isDraggingOver ? 'rgba(0,168,232,0.04)' : 'transparent',
        transition: 'all 0.15s ease',
      }}
    />
  );
}

function AddLeadCard({ onClick }: { onClick?: () => void }) {
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
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.15s ease',
        '&:hover': onClick ? {
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
  );
}

interface LeadPoolColumnProps {
  leads: Lead[];
  onAddLead?: () => void;
}

export default function LeadPoolColumn({ leads, onAddLead }: LeadPoolColumnProps) {
  const { t } = useTranslation();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minWidth: 272, maxWidth: 272, flexShrink: 0 }}>
      {/* Header */}
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        mb: 1.5, px: 0.5, pb: 1,
        borderBottom: '3px solid #00A8E8',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#00A8E8', flexShrink: 0 }} />
          <Typography sx={{
            fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 14, color: 'text.primary',
          }}>
            {t('pipeline.leadsPool')}
          </Typography>
        </Box>
        <Box sx={{
          px: 1, py: 0.2, borderRadius: '20px',
          bgcolor: 'rgba(0,168,232,0.1)', color: '#00A8E8',
          fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 700,
        }}>
          {leads.length}
        </Box>
      </Box>

      {/* Droppable area */}
      <Droppable droppableId={LEADS_POOL_ID}>
        {(provided, snapshot) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{ flex: 1, transition: 'all 0.15s ease' }}
          >
            {leads.map((lead, index) => (
              <LeadCard key={lead.id} lead={lead} index={index} />
            ))}
            {provided.placeholder}
            {leads.length === 0 && (
              <DropPlaceholder isDraggingOver={snapshot.isDraggingOver} />
            )}
          </Box>
        )}
      </Droppable>

      <AddLeadCard onClick={onAddLead} />
    </Box>
  );
}
