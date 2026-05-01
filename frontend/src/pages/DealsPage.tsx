import AddIcon from '@mui/icons-material/Add';
import { Alert, Box, Button, Skeleton, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { dealsApi } from '../api/deals';
import { pipelinesApi } from '../api/pipelines';
import AddDealDialog from '../components/deals/AddDealDialog';
import { type Deal, type DealStatus } from '../types/deal';
import { type Pipeline } from '../types/pipeline';

const DEMO_PIPELINE_ID = '00000000-0000-0000-0000-000000000001';

/* Stage name → i18n key (same mapping as KanbanColumn) */
const STAGE_I18N_KEYS: Record<string, string> = {
  'квалификация':          'deals.stages.qualification',
  'предложение':           'deals.stages.proposal',
  'переговоры':            'deals.stages.negotiation',
  'закрыто: победа':       'deals.stages.closed_won',
  'закрыто: проигрыш':     'deals.stages.closed_lost',
  'qualification':         'deals.stages.qualification',
  'proposal':              'deals.stages.proposal',
  'negotiation':           'deals.stages.negotiation',
  'closed won':            'deals.stages.closed_won',
  'closed lost':           'deals.stages.closed_lost',
};

function translateStageName(name: string, t: (k: string) => string): string {
  const key = STAGE_I18N_KEYS[name.trim().toLowerCase()];
  return key ? t(key) : name;
}

const STATUS_STYLE: Record<DealStatus, { bg: string; color: string }> = {
  open: { bg: 'rgba(0,168,232,0.10)',   color: '#00A8E8' },
  won:  { bg: 'rgba(16,185,129,0.10)',  color: '#059669' },
  lost: { bg: 'rgba(239,68,68,0.10)',   color: '#DC2626' },
};

export default function DealsPage() {
  const { t } = useTranslation();

  const [deals, setDeals] = useState<Deal[]>([]);
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      dealsApi.list(),
      pipelinesApi.get(DEMO_PIPELINE_ID),
    ])
      .then(([d, p]) => { setDeals(d); setPipeline(p); })
      .catch(() => setError(t('deals.loadError')))
      .finally(() => setLoading(false));
  }, [t]);

  /* When a new deal is created via the dialog, prepend it to the list */
  const handleDealCreated = (deal: Deal) => {
    setDeals((prev) => [deal, ...prev]);
  };

  /* Resolve stage name for a deal using loaded pipeline stages */
  const getStageName = (stageId: string): string => {
    const stage = pipeline?.stages.find((s) => s.id === stageId);
    return stage ? translateStageName(stage.name, t) : '—';
  };

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
          onClick={() => setDialogOpen(true)}
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
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
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
              {([
                [t('deals.table.title'),     undefined],
                [t('deals.table.amount'),    undefined],
                [t('deals.table.stage'),     undefined],
                [t('deals.table.status') || 'Status', '120px'],
                [t('deals.table.closeDate'), undefined],
              ] as [string, string | undefined][]).map(([label, width], i) => (
                <TableCell
                  key={i}
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    fontWeight: 500,
                    letterSpacing: '0.07em',
                    textTransform: 'uppercase',
                    color: '#94A3B8',
                    border: 'none',
                    py: 1.5,
                    width,
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
                  sx={{ py: 8, border: 'none', fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#94A3B8' }}
                >
                  {t('deals.noDeals')}
                </TableCell>
              </TableRow>
            ) : (
              deals.map((deal) => {
                const st = STATUS_STYLE[deal.status] ?? STATUS_STYLE.open;
                const amountNum = parseFloat(deal.value_amount);
                return (
                  <TableRow
                    key={deal.id}
                    sx={{
                      height: 56,
                      '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                      '&:hover': { bgcolor: '#F0F5FF' },
                    }}
                  >
                    {/* Title */}
                    <TableCell>
                      <Box>
                        <Typography sx={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 14, color: '#0D2144', lineHeight: 1.2 }}>
                          {deal.title}
                        </Typography>
                        {deal.company && (
                          <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8' }}>
                            {deal.company}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>

                    {/* Amount */}
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 14, color: '#00A8E8' }}>
                        {isNaN(amountNum) ? deal.value_amount : amountNum.toLocaleString()} {deal.value_currency}
                      </Typography>
                    </TableCell>

                    {/* Stage (resolved from pipeline) */}
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569' }}>
                        {getStageName(deal.stage_id)}
                      </Typography>
                    </TableCell>

                    {/* Status badge */}
                    <TableCell>
                      <Box sx={{
                        display: 'inline-flex', px: 1.25, py: 0.4, borderRadius: '20px',
                        bgcolor: st.bg, color: st.color, fontFamily: 'Inter', fontSize: 12, fontWeight: 600,
                      }}>
                        {t(`deals.status.${deal.status}`)}
                      </Box>
                    </TableCell>

                    {/* Close date */}
                    <TableCell>
                      <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
                        {deal.expected_close_date
                          ? new Date(deal.expected_close_date).toLocaleDateString()
                          : '—'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Box>

      {/* Add Deal Dialog */}
      <AddDealDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        pipeline={pipeline}
        onDealCreated={handleDealCreated}
      />
    </Box>
  );
}
