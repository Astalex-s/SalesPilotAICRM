import AddIcon from '@mui/icons-material/Add';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { Alert, Box, Button, CircularProgress, Skeleton, Table, TableBody, TableCell, TableHead, TableRow, Tooltip, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { dealsApi } from '../api/deals';
import { pipelinesApi } from '../api/pipelines';
import EmptyState from '../components/common/EmptyState';
import AddDealDialog from '../components/deals/AddDealDialog';
import DealActivitiesDialog from '../components/deals/DealActivitiesDialog';
import DealAttachmentsDialog from '../components/deals/DealAttachmentsDialog';
import { type Deal, type DealStatus } from '../types/deal';
import { type Pipeline } from '../types/pipeline';


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
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [closingId, setClosingId] = useState<string | null>(null);
  const [attachmentsDeal, setAttachmentsDeal] = useState<Deal | null>(null);
  const [activitiesDeal, setActivitiesDeal] = useState<Deal | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      dealsApi.list(),
      pipelinesApi.list(),
    ])
      .then(([d, p]) => { setDeals(d); setPipelines(p); })
      .catch(() => setError(t('deals.loadError')))
      .finally(() => setLoading(false));
  }, [t]);

  /* When a new deal is created via the dialog, prepend it to the list */
  const handleDealCreated = (deal: Deal) => {
    setDeals((prev) => [deal, ...prev]);
  };

  const handleCloseDeal = async (dealId: string, outcome: 'won' | 'lost') => {
    setClosingId(dealId);
    try {
      const updated = await dealsApi.close(dealId, outcome);
      setDeals((prev) => prev.map((d) => d.id === dealId ? updated : d));
    } catch {
      setError(t('deals.close.closeError'));
    } finally {
      setClosingId(null);
    }
  };

  /* Resolve stage name for a deal using loaded pipeline stages */
  const getStageName = (stageId: string): string => {
    for (const p of pipelines) {
      const stage = p.stages.find((s) => s.id === stageId);
      if (stage) return translateStageName(stage.name, t);
    }
    return '—';
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
          overflowX: 'auto',
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
                ['', '96px'],
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
                  {Array.from({ length: 6 }).map((__, j) => (
                    <TableCell key={j} sx={{ border: 'none', borderTop: '1px solid #F0F5FF' }}>
                      <Skeleton variant="text" width="80%" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : deals.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ border: 'none' }}>
                  <EmptyState
                    icon="deals"
                    title={t('deals.noDeals')}
                    subtitle={t('deals.noDealsSubtitle')}
                    action={{ label: t('deals.addDeal'), onClick: () => setDialogOpen(true) }}
                  />
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

                    {/* Actions — attachments + Won / Lost buttons */}
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                        <Tooltip title={t('deals.comments.title')}>
                          <Box
                            component="button"
                            onClick={() => setActivitiesDeal(deal)}
                            sx={{
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              width: 28, height: 28, borderRadius: '6px',
                              border: '1px solid #E8EFF7', bgcolor: '#FAFBFD',
                              color: '#8FA3B8', cursor: 'pointer',
                              '&:hover': { bgcolor: '#F0F5FF', color: '#00A8E8', borderColor: '#C8D9EC' },
                            }}
                          >
                            <ChatBubbleOutlineIcon sx={{ fontSize: 15 }} />
                          </Box>
                        </Tooltip>
                        <Tooltip title={t('attachments.title')}>
                          <Box
                            component="button"
                            onClick={() => setAttachmentsDeal(deal)}
                            sx={{
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              width: 28, height: 28, borderRadius: '6px',
                              border: '1px solid #E8EFF7', bgcolor: '#FAFBFD',
                              color: '#8FA3B8', cursor: 'pointer',
                              '&:hover': { bgcolor: '#F0F5FF', color: '#00A8E8', borderColor: '#C8D9EC' },
                            }}
                          >
                            <AttachFileIcon sx={{ fontSize: 15 }} />
                          </Box>
                        </Tooltip>
                      </Box>
                      {deal.status === 'open' && (
                        <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                          {closingId === deal.id ? (
                            <CircularProgress size={18} sx={{ color: '#00A8E8' }} />
                          ) : (
                            <>
                              <Tooltip title={t('deals.close.markWon')}>
                                <Box
                                  component="button"
                                  onClick={() => handleCloseDeal(deal.id, 'won')}
                                  sx={{
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    width: 28, height: 28, borderRadius: '6px',
                                    border: '1px solid #D1FAE5', bgcolor: '#F0FDF4',
                                    color: '#10B981', cursor: 'pointer',
                                    '&:hover': { bgcolor: '#D1FAE5' },
                                  }}
                                >
                                  <CheckIcon sx={{ fontSize: 15 }} />
                                </Box>
                              </Tooltip>
                              <Tooltip title={t('deals.close.markLost')}>
                                <Box
                                  component="button"
                                  onClick={() => handleCloseDeal(deal.id, 'lost')}
                                  sx={{
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    width: 28, height: 28, borderRadius: '6px',
                                    border: '1px solid #FEE2E2', bgcolor: '#FFF5F5',
                                    color: '#EF4444', cursor: 'pointer',
                                    '&:hover': { bgcolor: '#FEE2E2' },
                                  }}
                                >
                                  <CloseIcon sx={{ fontSize: 15 }} />
                                </Box>
                              </Tooltip>
                            </>
                          )}
                        </Box>
                      )}
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
        pipeline={pipelines[0] ?? null}
        onDealCreated={handleDealCreated}
      />

      {/* Attachments Dialog */}
      {attachmentsDeal && (
        <DealAttachmentsDialog
          open={Boolean(attachmentsDeal)}
          onClose={() => setAttachmentsDeal(null)}
          dealId={attachmentsDeal.id}
          dealTitle={attachmentsDeal.title}
        />
      )}

      {/* Comments / Activities Dialog */}
      <DealActivitiesDialog
        deal={activitiesDeal}
        open={Boolean(activitiesDeal)}
        onClose={() => setActivitiesDeal(null)}
      />
    </Box>
  );
}
