import { Box, Chip, Paper, Typography } from '@mui/material';
import { Droppable } from 'react-beautiful-dnd';
import { type Deal } from '../../types/deal';
import { type Stage } from '../../types/pipeline';
import DealCard from './DealCard';

interface KanbanColumnProps {
  stage: Stage;
  deals: Deal[];
}

export default function KanbanColumn({ stage, deals }: KanbanColumnProps) {
  const totalValue = deals
    .filter((d) => d.status === 'open')
    .reduce((sum, d) => sum + Number(d.value_amount), 0);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minWidth: 280,
        maxWidth: 280,
        flexShrink: 0,
      }}
    >
      {/* Column header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 1,
          px: 0.5,
        }}
      >
        <Typography variant="subtitle1" fontWeight={700}>
          {stage.name}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <Chip label={deals.length} size="small" />
          {totalValue > 0 && (
            <Typography variant="caption" color="success.main" fontWeight={600}>
              ${totalValue.toLocaleString()}
            </Typography>
          )}
        </Box>
      </Box>

      {/* Droppable area */}
      <Droppable droppableId={stage.id}>
        {(provided, snapshot) => (
          <Paper
            ref={provided.innerRef}
            {...provided.droppableProps}
            variant="outlined"
            sx={{
              p: 1,
              minHeight: 120,
              flexGrow: 1,
              bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'background.paper',
              transition: 'background-color 0.15s ease',
            }}
          >
            {deals.map((deal, index) => (
              <DealCard key={deal.id} deal={deal} index={index} />
            ))}
            {provided.placeholder}
          </Paper>
        )}
      </Droppable>
    </Box>
  );
}
