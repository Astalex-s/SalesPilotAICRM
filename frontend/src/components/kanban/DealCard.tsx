import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import BusinessIcon from '@mui/icons-material/Business';
import { Box, Card, CardContent, Chip, Typography } from '@mui/material';
import { Draggable } from 'react-beautiful-dnd';
import { type Deal } from '../../types/deal';

interface DealCardProps {
  deal: Deal;
  index: number;
}

const STATUS_COLOR: Record<Deal['status'], 'default' | 'success' | 'error'> = {
  open: 'default',
  won: 'success',
  lost: 'error',
};

const STATUS_LABEL: Record<Deal['status'], string> = {
  open: 'Открыта',
  won: 'Выиграна',
  lost: 'Проиграна',
};

export default function DealCard({ deal, index }: DealCardProps) {
  return (
    <Draggable draggableId={deal.id} index={index} isDragDisabled={deal.status !== 'open'}>
      {(provided, snapshot) => (
        <Card
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          elevation={snapshot.isDragging ? 6 : 1}
          sx={{
            mb: 1,
            cursor: deal.status === 'open' ? 'grab' : 'not-allowed',
            opacity: deal.status !== 'open' ? 0.6 : 1,
            transition: 'box-shadow 0.15s ease',
            '&:active': { cursor: 'grabbing' },
          }}
        >
          <CardContent sx={{ p: '12px !important' }}>
            <Typography variant="subtitle2" fontWeight={600} noWrap>
              {deal.title}
            </Typography>

            {deal.company && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                <BusinessIcon sx={{ fontSize: 13, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary" noWrap>
                  {deal.company}
                </Typography>
              </Box>
            )}

            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }}>
                <AttachMoneyIcon sx={{ fontSize: 14, color: 'success.main' }} />
                <Typography variant="caption" fontWeight={500} color="success.main">
                  {Number(deal.value_amount).toLocaleString()} {deal.value_currency}
                </Typography>
              </Box>
              <Chip
                label={STATUS_LABEL[deal.status]}
                color={STATUS_COLOR[deal.status]}
                size="small"
                sx={{ height: 18, fontSize: 10 }}
              />
            </Box>
          </CardContent>
        </Card>
      )}
    </Draggable>
  );
}
