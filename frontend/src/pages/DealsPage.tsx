import AddIcon from '@mui/icons-material/Add';
import { Alert, Box, Button, Skeleton, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { type DealStage } from '../types/deal';

const STAGE_STYLE: Record<DealStage, { bg: string; color: string }> = {
  qualification: { bg: 'rgba(0,168,232,0.12)',  color: '#0090CC' },
  proposal:      { bg: 'rgba(245,158,11,0.12)', color: '#D97706' },
  negotiation:   { bg: 'rgba(139,92,246,0.12)', color: '#7C3AED' },
  closed_won:    { bg: 'rgba(16,185,129,0.12)', color: '#059669' },
  closed_lost:   { bg: 'rgba(239,68,68,0.12)',  color: '#DC2626' },
};

export default function DealsPage() {
  const { t } = useTranslation();

  // Placeholder — data fetching will be wired in a future step
  const loading = false;
  const error: string | null = null;
  const deals: never[] = [];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144' }}>
          {t('deals.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          disabled
          sx={{
            bgcolor: '#00A8E8',
            color: '#fff',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 14,
            borderRadius: '10px',
            px: 2.5,
            textTransform: 'none',
            boxShadow: 'none',
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {t('deals.addDeal')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

      {/* Table card */}
      <Box
        sx={{
          background: '#FFFFFF',
          border: '1px solid #E2EAF4',
          borderRadius: '16px',
          boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
        }}
      >
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {[
                t('deals.table.title'),
                t('deals.table.amount'),
                t('deals.table.stage'),
                t('deals.table.closeDate'),
                t('deals.table.created'),
              ].map((label) => (
                <TableCell
                  key={label}
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    fontWeight: 500,
                    letterSpacing: '0.07em',
                    textTransform: 'uppercase',
                    color: '#94A3B8',
                    border: 'none',
                    py: 1.5,
                  }}
                >
                  {label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i} sx={{ height: 56 }}>
                  {Array.from({ length: 5 }).map((__, j) => (
                    <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                      <Skeleton variant="text" width="80%" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : deals.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  align="center"
                  sx={{
                    py: 8,
                    border: 'none',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    color: '#94A3B8',
                  }}
                >
                  {t('deals.noDeals')}
                </TableCell>
              </TableRow>
            ) : (
              deals.map((deal) => {
                const d = deal as {
                  id: string;
                  title: string;
                  amount: number;
                  stage: DealStage;
                  close_date: string | null;
                  created_at: string;
                };
                const s = STAGE_STYLE[d.stage];
                return (
                  <TableRow
                    key={d.id}
                    sx={{
                      height: 56,
                      '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                      '&:hover': { bgcolor: '#F0F5FF' },
                    }}
                  >
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: '#0D2144' }}>
                        {d.title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 14, color: '#00A8E8' }}>
                        ${d.amount.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box
                        sx={{
                          display: 'inline-flex',
                          px: 1.25,
                          py: 0.4,
                          borderRadius: '20px',
                          bgcolor: s.bg,
                          color: s.color,
                          fontFamily: 'Inter',
                          fontSize: 12,
                          fontWeight: 600,
                        }}
                      >
                        {t(`deals.stages.${d.stage}`)}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
                        {d.close_date ? new Date(d.close_date).toLocaleDateString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
                        {new Date(d.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Box>
    </Box>
  );
}
