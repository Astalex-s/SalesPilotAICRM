import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { aiApi } from '../../api/ai';
import { dealsApi } from '../../api/deals';
import { gmailApi } from '../../api/gmail';
import { useAuthStore } from '../../store/useAuthStore';
import { useLeadStore } from '../../store/useLeadStore';
import type { LeadStatus } from '../../types/lead';
import type { LeadScore, NextBestAction } from '../../types/ai';
import type { Deal } from '../../types/deal';
import type { Lead } from '../../types/lead';
import type { Pipeline, Stage } from '../../types/pipeline';

const DEMO_PIPELINE_ID = '00000000-0000-0000-0000-000000000001';

/* ── helpers ──────────────────────────────────────────────────────────────── */
const cardSx = {
  border: '1px solid #E8EFF7',
  borderRadius: '12px',
  p: 2.5,
  bgcolor: '#FAFBFD',
};

const sectionTitle = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 13,
  fontWeight: 700,
  color: '#0D2144',
  mb: 0.5,
};

function ScoreGauge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? '#059669' : pct >= 40 ? '#D97706' : '#DC2626';
  const r = 28;
  const circ = 2 * Math.PI * r;
  return (
    <Box sx={{ position: 'relative', width: 72, height: 72, flexShrink: 0 }}>
      <svg width="72" height="72" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="36" cy="36" r={r} fill="none" stroke="#E8EFF7" strokeWidth="6" />
        <circle
          cx="36" cy="36" r={r} fill="none"
          stroke={color} strokeWidth="6"
          strokeDasharray={`${(pct / 100) * circ} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <Box sx={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 800, fontSize: 16, color }}>
          {pct}
        </Typography>
      </Box>
    </Box>
  );
}

/* ── AI Score Card ──────────────────────────────────────────────────────────── */
function AiScoreCard({ lead }: { lead: Lead }) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState<LeadScore | null>(null);
  const [nba, setNba] = useState<NextBestAction | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, n] = await Promise.all([
        aiApi.scoreLead(lead.id),
        aiApi.nextBestAction(lead.id),
      ]);
      setScore(s);
      setNba(n);
    } catch {
      setError(t('deals.success.aiCard.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={cardSx}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        {/* spark icon */}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00A8E8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
        </svg>
        <Typography sx={sectionTitle}>{t('deals.success.aiCard.title')}</Typography>
      </Box>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#64748B', mb: 1.5 }}>
        {t('deals.success.aiCard.desc')}
      </Typography>

      {!score && !loading && (
        <Button
          size="small"
          variant="outlined"
          onClick={analyze}
          sx={{
            fontFamily: 'Inter', fontSize: 12, fontWeight: 600, textTransform: 'none',
            borderColor: '#00A8E8', color: '#00A8E8', borderRadius: '8px',
            '&:hover': { borderColor: '#0090CC', bgcolor: 'rgba(0,168,232,0.05)' },
          }}
        >
          {t('deals.success.aiCard.button')}
        </Button>
      )}

      {loading && <CircularProgress size={20} sx={{ color: '#00A8E8' }} />}
      {error && <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#DC2626' }}>{error}</Typography>}

      {score && !loading && (
        <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start', mt: 0.5 }}>
          <ScoreGauge value={score.score} />
          <Box sx={{ flex: 1 }}>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
              {score.reasoning}
            </Typography>
            {nba && (
              <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(0,168,232,0.06)', borderRadius: '8px' }}>
                <Typography sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 700, color: '#00A8E8', mb: 0.25 }}>
                  {nba.action}
                </Typography>
                <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#64748B' }}>
                  {nba.reasoning}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Email Card ─────────────────────────────────────────────────────────────── */
function EmailCard({ lead }: { lead: Lead }) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [genLoading, setGenLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateEmail = async () => {
    setGenLoading(true);
    setError(null);
    try {
      const result = await aiApi.generateEmail(lead.id, 'friendly');
      setSubject(result.subject);
      setBody(result.body);
    } catch {
      setError(t('deals.success.emailCard.error'));
    } finally {
      setGenLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!subject || !body) return;
    setSending(true);
    setError(null);
    try {
      await gmailApi.sendEmail({
        to: lead.email,
        subject,
        body,
        performed_by_id: user?.id ?? '',
        lead_id: lead.id,
      });
      setSent(true);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === 401 || status === 403) {
        setError('notConnected');
      } else {
        setError(t('deals.success.emailCard.error'));
      }
    } finally {
      setSending(false);
    }
  };

  return (
    <Box sx={cardSx}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00A8E8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6" />
        </svg>
        <Typography sx={sectionTitle}>{t('deals.success.emailCard.title')}</Typography>
      </Box>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#64748B', mb: 1.5 }}>
        {t('deals.success.emailCard.desc')}
      </Typography>

      {sent ? (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: '#059669' }}>
            {t('deals.success.emailCard.sent')}
          </Typography>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {/* To (readonly) */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', minWidth: 42 }}>
              {t('deals.success.emailCard.to')}:
            </Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#0D2144', fontWeight: 500 }}>
              {lead.email}
            </Typography>
          </Box>

          {/* Subject */}
          <TextField
            size="small"
            label={t('deals.success.emailCard.subject')}
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            sx={{ '& .MuiInputBase-root': { fontFamily: 'Inter', fontSize: 12, borderRadius: '8px' }, '& label': { fontFamily: 'Inter', fontSize: 12 } }}
          />

          {/* Body */}
          <TextField
            size="small"
            multiline
            rows={3}
            label={t('deals.success.emailCard.body')}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            sx={{ '& .MuiInputBase-root': { fontFamily: 'Inter', fontSize: 12, borderRadius: '8px' }, '& label': { fontFamily: 'Inter', fontSize: 12 } }}
          />

          {error === 'notConnected' ? (
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#DC2626' }}>
              {t('deals.success.emailCard.notConnected')}{' '}
              <a href="/gmail" style={{ color: '#00A8E8', textDecoration: 'none', fontWeight: 600 }}>
                {t('deals.success.emailCard.connectLink')}
              </a>
            </Typography>
          ) : error ? (
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#DC2626' }}>{error}</Typography>
          ) : null}

          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              size="small"
              variant="outlined"
              onClick={generateEmail}
              disabled={genLoading}
              sx={{
                fontFamily: 'Inter', fontSize: 11, fontWeight: 600, textTransform: 'none',
                borderColor: '#00A8E8', color: '#00A8E8', borderRadius: '8px',
                '&:hover': { borderColor: '#0090CC', bgcolor: 'rgba(0,168,232,0.05)' },
                '&.Mui-disabled': { borderColor: '#CBD5E8', color: '#CBD5E8' },
              }}
            >
              {genLoading ? t('deals.success.emailCard.generating') : t('deals.success.emailCard.generateAI')}
            </Button>
            <Button
              size="small"
              variant="contained"
              onClick={sendEmail}
              disabled={sending || !subject || !body}
              sx={{
                bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontSize: 11, fontWeight: 600,
                textTransform: 'none', borderRadius: '8px', boxShadow: 'none',
                '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
                '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
              }}
            >
              {sending ? t('deals.success.emailCard.sending') : t('deals.success.emailCard.send')}
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Telegram Info Card ─────────────────────────────────────────────────────── */
function TelegramCard() {
  const { t } = useTranslation();
  return (
    <Box sx={cardSx}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00A8E8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 2L11 13 M22 2L15 22l-4-9-9-4 22-9z" />
        </svg>
        <Typography sx={sectionTitle}>{t('deals.success.telegramCard.title')}</Typography>
      </Box>
      <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#64748B', lineHeight: 1.6 }}>
        {t('deals.success.telegramCard.desc')}
      </Typography>
      <Box sx={{
        mt: 1.25, display: 'inline-flex', alignItems: 'center', gap: 0.75,
        px: 1.25, py: 0.4, bgcolor: 'rgba(0,168,232,0.08)', borderRadius: '8px',
      }}>
        <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#059669' }} />
        <Typography sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 600, color: '#059669' }}>
          Auto
        </Typography>
      </Box>
    </Box>
  );
}

/* ── Success Step ───────────────────────────────────────────────────────────── */
interface SuccessStepProps {
  deal: Deal;
  lead: Lead;
  pipelineId: string;
  onDone: () => void;
}

function SuccessStep({ deal, lead, pipelineId, onDone }: SuccessStepProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <Box>
      {/* Success header */}
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <Box sx={{
          width: 52, height: 52, borderRadius: '50%',
          bgcolor: 'rgba(16,185,129,0.1)', mx: 'auto', mb: 1.5,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </Box>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 18, color: '#0D2144', mb: 0.5 }}>
          {t('deals.success.title')}
        </Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#64748B' }}>
          {t('deals.success.subtitle', { title: deal.title })}
        </Typography>
      </Box>

      {/* Action cards */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        <AiScoreCard lead={lead} />
        <EmailCard lead={lead} />
        <TelegramCard />
      </Box>

      {/* Buttons */}
      <Box sx={{ display: 'flex', gap: 1.5, mt: 3, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          onClick={() => navigate(`/pipeline/${pipelineId}`)}
          sx={{
            fontFamily: 'Inter', fontSize: 13, fontWeight: 600, textTransform: 'none',
            borderColor: '#E8EFF7', color: '#0D2144', borderRadius: '10px',
            '&:hover': { borderColor: '#00A8E8', color: '#00A8E8' },
          }}
        >
          {t('deals.success.viewPipeline')}
        </Button>
        <Button
          variant="contained"
          onClick={onDone}
          sx={{
            bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '10px', textTransform: 'none', boxShadow: 'none',
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
          }}
        >
          {t('deals.success.done')}
        </Button>
      </Box>
    </Box>
  );
}

/* ── Form Step ──────────────────────────────────────────────────────────────── */
interface FormStepProps {
  leads: Lead[];
  pipeline: Pipeline | null;
  defaultStageId?: string;
  onCancel: () => void;
  onCreated: (deal: Deal, lead: Lead) => void;
  onLeadUpdated: (leadId: string, status: LeadStatus) => Promise<void>;
}

function FormStep({ leads, pipeline, defaultStageId, onCancel, onCreated, onLeadUpdated }: FormStepProps) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const [leadId, setLeadId] = useState('');
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('0');
  const [currency, setCurrency] = useState('USD');
  const [stageId, setStageId] = useState('');
  const [closeDate, setCloseDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [qualifying, setQualifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedLead = leads.find((l) => l.id === leadId) ?? null;
  const isNotQualified = selectedLead !== null && selectedLead.status !== 'qualified';

  const handleLeadChange = (id: string) => {
    setLeadId(id);
    const lead = leads.find((l) => l.id === id);
    if (lead) {
      setTitle(`${lead.first_name} ${lead.last_name}${lead.company ? ` — ${lead.company}` : ''}`);
    }
  };

  const stages: Stage[] = pipeline?.stages ?? [];

  // Auto-select defaultStageId or first stage when pipeline loads
  useEffect(() => {
    if (stageId === '' && stages.length > 0) {
      const preferred = defaultStageId && stages.find((s) => s.id === defaultStageId);
      setStageId(preferred ? preferred.id : stages[0].id);
    }
  }, [stages.length]);

  const handleSubmit = async () => {
    if (!leadId || !stageId) return;
    setSubmitting(true);
    setError(null);
    try {
      const deal = await dealsApi.create({
        lead_id: leadId,
        stage_id: stageId,
        pipeline_id: pipeline?.id ?? DEMO_PIPELINE_ID,
        deal_title: title || undefined,
        deal_value_amount: amount,
        deal_value_currency: currency,
        performed_by_id: user?.id,
      });
      onCreated(deal, selectedLead!);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(msg ?? t('deals.dialog.error'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleQualify = async () => {
    if (!leadId) return;
    setQualifying(true);
    setError(null);
    try {
      await onLeadUpdated(leadId, 'qualified');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('deals.dialog.error'));
    } finally {
      setQualifying(false);
    }
  };

  const canSubmit = !!leadId && !!stageId && !submitting && !isNotQualified;

  const inputSx = {
    '& .MuiInputBase-root': { fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' },
    '& label': { fontFamily: 'Inter', fontSize: 13 },
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Lead selector */}
      <FormControl size="small" fullWidth>
        <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('deals.dialog.leadLabel')}</InputLabel>
        <Select
          value={leadId}
          label={t('deals.dialog.leadLabel')}
          onChange={(e) => handleLeadChange(e.target.value)}
          sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
        >
          <MenuItem value="" disabled sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
            {t('deals.dialog.leadPlaceholder')}
          </MenuItem>
          {leads.map((l) => (
            <MenuItem key={l.id} value={l.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <span>{l.first_name} {l.last_name}{l.company ? ` — ${l.company}` : ''}</span>
                <Box sx={{
                  px: 0.75, py: 0.15, borderRadius: '6px', fontSize: 10, fontWeight: 700,
                  bgcolor: l.status === 'qualified' ? 'rgba(16,185,129,0.12)' : 'rgba(148,163,184,0.15)',
                  color: l.status === 'qualified' ? '#059669' : '#94A3B8',
                }}>
                  {t(`leads.status.${l.status}`)}
                </Box>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {isNotQualified && (
        <Alert
          severity="warning"
          sx={{ borderRadius: '8px', py: 0.5, '& .MuiAlert-message': { fontFamily: 'Inter', fontSize: 12, width: '100%' } }}
          action={
            <Button
              size="small"
              onClick={handleQualify}
              disabled={qualifying}
              sx={{
                fontFamily: 'Inter', fontSize: 11, fontWeight: 700, textTransform: 'none',
                color: '#D97706', borderColor: '#D97706', borderRadius: '6px',
                whiteSpace: 'nowrap',
                '&:hover': { bgcolor: 'rgba(217,119,6,0.08)' },
              }}
            >
              {qualifying
                ? <><CircularProgress size={11} sx={{ color: '#D97706', mr: 0.5 }} />{t('deals.dialog.qualifying')}</>
                : t('deals.dialog.qualifyLead')
              }
            </Button>
          }
        >
          {t('deals.dialog.notQualifiedWarning')}
        </Alert>
      )}

      {/* Deal title */}
      <TextField
        size="small"
        label={t('deals.dialog.titleLabel')}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        fullWidth
        sx={inputSx}
      />

      {/* Amount + currency */}
      <Box sx={{ display: 'flex', gap: 1.5 }}>
        <TextField
          size="small"
          label={t('deals.dialog.amountLabel')}
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          sx={{ ...inputSx, flex: 1 }}
          inputProps={{ min: 0 }}
        />
        <FormControl size="small" sx={{ width: 110 }}>
          <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('deals.dialog.currencyLabel')}</InputLabel>
          <Select
            value={currency}
            label={t('deals.dialog.currencyLabel')}
            onChange={(e) => setCurrency(e.target.value)}
            sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
          >
            {['USD', 'EUR', 'RUB', 'GBP'].map((c) => (
              <MenuItem key={c} value={c} sx={{ fontFamily: 'Inter', fontSize: 13 }}>{c}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Stage */}
      <FormControl size="small" fullWidth>
        <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('deals.dialog.stageLabel')}</InputLabel>
        <Select
          value={stageId}
          label={t('deals.dialog.stageLabel')}
          onChange={(e) => setStageId(e.target.value)}
          sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
        >
          {stages.map((s) => (
            <MenuItem key={s.id} value={s.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
              {s.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Close date */}
      <TextField
        size="small"
        label={t('deals.dialog.closeDateLabel')}
        type="date"
        value={closeDate}
        onChange={(e) => setCloseDate(e.target.value)}
        fullWidth
        sx={inputSx}
        InputLabelProps={{ shrink: true }}
      />

      {error && (
        <Alert severity="error" sx={{ borderRadius: '8px', py: 0.5, '& .MuiAlert-message': { fontFamily: 'Inter', fontSize: 12 } }}>
          {error}
        </Alert>
      )}

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end', pt: 0.5 }}>
        <Button
          variant="outlined"
          onClick={onCancel}
          sx={{
            fontFamily: 'Inter', fontSize: 13, fontWeight: 500, textTransform: 'none',
            borderColor: '#E8EFF7', color: '#64748B', borderRadius: '10px',
            '&:hover': { borderColor: '#CBD5E8', bgcolor: 'transparent' },
          }}
        >
          {t('deals.dialog.cancel')}
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!canSubmit}
          sx={{
            bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '10px', textTransform: 'none', boxShadow: 'none',
            minWidth: 130,
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {submitting
            ? <><CircularProgress size={14} sx={{ color: '#fff', mr: 1 }} />{t('deals.dialog.submitting')}</>
            : t('deals.dialog.submit')
          }
        </Button>
      </Box>
    </Box>
  );
}

/* ── Main Dialog ────────────────────────────────────────────────────────────── */
interface AddDealDialogProps {
  open: boolean;
  onClose: () => void;
  pipeline: Pipeline | null;
  onDealCreated: (deal: Deal) => void;
  defaultStageId?: string;
}

export default function AddDealDialog({ open, onClose, pipeline, onDealCreated, defaultStageId }: AddDealDialogProps) {
  const { t } = useTranslation();
  const leads = useLeadStore((s) => s.leads);
  const fetchLeads = useLeadStore((s) => s.fetchLeads);
  const updateLeadInStore = useLeadStore((s) => s.updateLead);

  const [step, setStep] = useState<'form' | 'success'>('form');
  const [createdDeal, setCreatedDeal] = useState<Deal | null>(null);
  const [createdLead, setCreatedLead] = useState<Lead | null>(null);

  // Load leads when dialog opens
  useEffect(() => {
    if (open && leads.length === 0) fetchLeads();
  }, [open]);

  const handleCreated = (deal: Deal, lead: Lead) => {
    setCreatedDeal(deal);
    setCreatedLead(lead);
    setStep('success');
    onDealCreated(deal);
  };

  const handleClose = () => {
    onClose();
    // Reset state after animation completes
    setTimeout(() => {
      setStep('form');
      setCreatedDeal(null);
      setCreatedLead(null);
    }, 300);
  };

  return (
    <Dialog
      open={open}
      onClose={step === 'form' ? handleClose : undefined}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '16px',
          boxShadow: '0 8px 40px rgba(13,33,68,0.12)',
          overflow: 'hidden',
        },
      }}
    >
      {/* Header */}
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        px: 3, py: 2, borderBottom: '1px solid #E8EFF7',
      }}>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 16, color: '#0D2144' }}>
          {step === 'form' ? t('deals.dialog.title') : t('deals.success.title')}
        </Typography>
        {step === 'form' && (
          <Box
            onClick={handleClose}
            sx={{ cursor: 'pointer', color: '#94A3B8', display: 'flex', '&:hover': { color: '#0D2144' } }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18 M6 6l12 12" />
            </svg>
          </Box>
        )}
      </Box>

      <DialogContent sx={{ p: 3 }}>
        {step === 'form' ? (
          <FormStep
            leads={leads}
            pipeline={pipeline}
            defaultStageId={defaultStageId}
            onCancel={handleClose}
            onCreated={handleCreated}
            onLeadUpdated={async (id, status) => { await updateLeadInStore(id, { status }); }}
          />
        ) : (
          <SuccessStep
            deal={createdDeal!}
            lead={createdLead!}
            pipelineId={pipeline?.id ?? DEMO_PIPELINE_ID}
            onDone={handleClose}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
