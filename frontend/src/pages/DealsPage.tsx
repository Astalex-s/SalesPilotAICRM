import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { type DealStage } from '../types/deal';

const STAGE_COLOR: Record<DealStage, 'default' | 'info' | 'success' | 'error' | 'warning'> = {
  qualification: 'info',
  proposal: 'warning',
  negotiation: 'warning',
  closed_won: 'success',
  closed_lost: 'error',
};

export default function DealsPage() {
  // Placeholder — data fetching will be wired in STEP 12
  const loading = false;
  const error: string | null = null;
  const deals: never[] = [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">Сделки</Typography>
        <Button variant="contained" disabled>
          + Новая сделка
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Название</TableCell>
                <TableCell>Сумма</TableCell>
                <TableCell>Этап</TableCell>
                <TableCell>Дата закрытия</TableCell>
                <TableCell>Создан</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {deals.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    Сделки не найдены.
                  </TableCell>
                </TableRow>
              ) : (
                deals.map((deal) => {
                  const d = deal as { id: string; title: string; amount: number; stage: DealStage; close_date: string | null; created_at: string };
                  return (
                    <TableRow key={d.id} hover>
                      <TableCell>{d.title}</TableCell>
                      <TableCell>${d.amount.toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip label={d.stage} color={STAGE_COLOR[d.stage]} size="small" />
                      </TableCell>
                      <TableCell>
                        {d.close_date ? new Date(d.close_date).toLocaleDateString() : '—'}
                      </TableCell>
                      <TableCell>
                        {new Date(d.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
