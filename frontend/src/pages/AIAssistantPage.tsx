import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { aiApi } from '../api/ai';
import { dealsApi } from '../api/deals';
import { useKanbanStore } from '../store/useKanbanStore';
import { useLeadStore } from '../store/useLeadStore';
import type { AiTone, DealForecast, GeneratedEmail, LeadScore, LostDealsAnalysis, NextBestAction, PipelineDigest } from '../types/ai';
import type { Deal } from '../types/deal';

/* ── shared style tokens ────────────────────────────────────────────────────── */
const card = {
  background: '#FFFFFF',
  border: '1px solid #E8EFF7',
  borderRadius: '12px',
  boxShadow: '0 1px 4px rgba(13,33,68,0.06)',
  p: 3,
};

const sectionTitle = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 13,
  fontWeight: 700,
  color: '#0D2144',
  mb: 1,
};

/* ── Priority pill ──────────────────────────────────────────────────────────── */
const PRIORITY_STYLE: Record<string, { bg: string; color: string }> = {
  high:   { bg: 'rgba(239,68,68,0.1)',   color: '#DC2626' },
  medium: { bg: 'rgba(245,158,11,0.1)',  color: '#D97706' },
  low:    { bg: 'rgba(16,185,129,0.1)',  color: '#059669' },
};

function PriorityPill({ priority, label }: { priority: string; label: string }) {
  const s = PRIORITY_STYLE[priority] ?? PRIORITY_STYLE.medium;
  return (
    <Box sx={{
      display: 'inline-flex', px: 1.25, py: 0.35,
      borderRadius: '20px', bgcolor: s.bg, color: s.color,
      fontFamily: 'Inter', fontSize: 11, fontWeight: 700,
    }}>
      {label}
    </Box>
  );
}

/* ── Circular score gauge ───────────────────────────────────────────────────── */
function ScoreGauge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? '#059669' : pct >= 40 ? '#D97706' : '#DC2626';
  const r = 36;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <Box sx={{ position: 'relative', width: 96, height: 96, flexShrink: 0 }}>
      <svg width="96" height="96" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="48" cy="48" r={r} fill="none" stroke="#E8EFF7" strokeWidth="8" />
        <circle
          cx="48" cy="48" r={r} fill="none"
          stroke={color} strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <Box sx={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 800, fontSize: 22, color, lineHeight: 1 }}>
          {pct}
        </Typography>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 10, color: '#8FA3B8', fontWeight: 500 }}>
          / 100
        </Typography>
      </Box>
    </Box>
  );
}

/* ── Lead Score Tab ─────────────────────────────────────────────────────────── */
function LeadScoreTab() {
  const { t } = useTranslation();
  const leads = useLeadStore((s) => s.leads);
  const fetchLeads = useLeadStore((s) => s.fetchLeads);
  useEffect(() => { if (leads.length === 0) fetchLeads(); }, []);
  const [leadId, setLeadId] = useState('');
  const [result, setResult] = useState<LeadScore | null>(null);
  const [nba, setNba] = useState<NextBestAction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!leadId) return;
    setLoading(true);
    setError(null);
    try {
      const [score, action] = await Promise.all([
        aiApi.scoreLead(leadId),
        aiApi.nextBestAction(leadId),
      ]);
      setResult(score);
      setNba(action);
    } catch {
      setError(t('aiAssistant.errors.score'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
      {/* Selector + button */}
      <Box sx={{ ...card, display: 'flex', gap: 2, alignItems: 'flex-end' }}>
        <FormControl size="small" sx={{ flex: 1 }}>
          <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('aiAssistant.selectLead')}</InputLabel>
          <Select
            value={leadId}
            label={t('aiAssistant.selectLead')}
            onChange={(e) => { setLeadId(e.target.value); setResult(null); setNba(null); }}
            sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
          >
            <MenuItem value="" disabled sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
              {t('aiAssistant.selectLeadPlaceholder')}
            </MenuItem>
            {leads.map((l) => (
              <MenuItem key={l.id} value={l.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                {l.first_name} {l.last_name} {l.company ? `— ${l.company}` : ''}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button
          variant="contained"
          onClick={analyze}
          disabled={!leadId || loading}
          sx={{
            bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '8px', textTransform: 'none', boxShadow: 'none',
            px: 2.5, height: 40, whiteSpace: 'nowrap',
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {loading ? t('aiAssistant.analyzing') : t('aiAssistant.analyze')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ borderRadius: '10px' }}>{error}</Alert>}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress sx={{ color: '#00A8E8' }} />
        </Box>
      )}

      {result && !loading && (
        <Box sx={{ display: 'flex', gap: 2.5, flexWrap: 'wrap' }}>
          {/* Score gauge card */}
          <Box sx={{ ...card, flex: '1 1 260px', display: 'flex', gap: 2.5, alignItems: 'flex-start' }}>
            <ScoreGauge value={result.score} />
            <Box sx={{ flex: 1 }}>
              <Typography sx={{ ...sectionTitle, mb: 0.5 }}>{t('aiAssistant.score.title')}</Typography>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                {result.reasoning}
              </Typography>
            </Box>
          </Box>

          {/* Recommended actions */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.score.actions')}</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {result.recommended_actions.map((action, i) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Box sx={{
                    mt: 0.6, width: 6, height: 6, borderRadius: '50%',
                    bgcolor: '#00A8E8', flexShrink: 0,
                  }} />
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                    {action}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Next best action */}
          {nba && (
            <Box sx={{ ...card, flex: '1 1 100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                <Typography sx={sectionTitle}>{t('leadDetail.ai.actions')}</Typography>
                <PriorityPill
                  priority={nba.priority}
                  label={t(`aiAssistant.priority.${nba.priority}`)}
                />
              </Box>
              <Typography sx={{
                fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: '#0D2144', mb: 0.75,
              }}>
                {nba.action}
              </Typography>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                {nba.reasoning}
              </Typography>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}

/* ── Deal Forecast Tab ──────────────────────────────────────────────────────── */
function DealForecastTab() {
  const { t } = useTranslation();
  const [deals, setDeals] = useState<Deal[]>([]);
  useEffect(() => { dealsApi.list().then(setDeals).catch(() => {}); }, []);
  const [dealId, setDealId] = useState('');
  const [result, setResult] = useState<DealForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!dealId) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await aiApi.forecastDeal(dealId));
    } catch {
      setError(t('aiAssistant.errors.forecast'));
    } finally {
      setLoading(false);
    }
  };

  const pct = result ? Math.round(result.win_probability * 100) : 0;
  const barColor = pct >= 70 ? '#059669' : pct >= 40 ? '#D97706' : '#DC2626';

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
      <Box sx={{ ...card, display: 'flex', gap: 2, alignItems: 'flex-end' }}>
        <FormControl size="small" sx={{ flex: 1 }}>
          <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('aiAssistant.selectDeal')}</InputLabel>
          <Select
            value={dealId}
            label={t('aiAssistant.selectDeal')}
            onChange={(e) => { setDealId(e.target.value); setResult(null); }}
            sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
          >
            <MenuItem value="" disabled sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
              {t('aiAssistant.selectDealPlaceholder')}
            </MenuItem>
            {deals.map((d) => (
              <MenuItem key={d.id} value={d.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                {d.title} — ${parseFloat(d.value_amount).toLocaleString()}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button
          variant="contained"
          onClick={analyze}
          disabled={!dealId || loading}
          sx={{
            bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '8px', textTransform: 'none', boxShadow: 'none',
            px: 2.5, height: 40, whiteSpace: 'nowrap',
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {loading ? t('aiAssistant.analyzing') : t('aiAssistant.analyze')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ borderRadius: '10px' }}>{error}</Alert>}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress sx={{ color: '#00A8E8' }} />
        </Box>
      )}

      {result && !loading && (
        <Box sx={{ display: 'flex', gap: 2.5, flexWrap: 'wrap' }}>
          {/* Win probability bar */}
          <Box sx={{ ...card, flex: '1 1 280px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.forecast.title')}</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1.5 }}>
              <Box sx={{ flex: 1, height: 10, bgcolor: '#E8EFF7', borderRadius: '8px', overflow: 'hidden' }}>
                <Box sx={{
                  width: `${pct}%`, height: '100%',
                  bgcolor: barColor, borderRadius: '8px',
                  transition: 'width 0.6s ease',
                }} />
              </Box>
              <Typography sx={{ fontFamily: 'Inter', fontWeight: 800, fontSize: 20, color: barColor, minWidth: 52 }}>
                {pct}%
              </Typography>
            </Box>
          </Box>

          {/* Risk factors */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.forecast.risks')}</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
              {result.risk_factors.map((r, i) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Box sx={{ mt: 0.6, width: 6, height: 6, borderRadius: '50%', bgcolor: '#DC2626', flexShrink: 0 }} />
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                    {r}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Opportunities */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.forecast.opportunities')}</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
              {result.opportunities.map((o, i) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Box sx={{ mt: 0.6, width: 6, height: 6, borderRadius: '50%', bgcolor: '#059669', flexShrink: 0 }} />
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                    {o}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Email Generator Tab ────────────────────────────────────────────────────── */
function EmailGenTab() {
  const { t } = useTranslation();
  const leads = useLeadStore((s) => s.leads);
  const fetchLeads = useLeadStore((s) => s.fetchLeads);
  useEffect(() => { if (leads.length === 0) fetchLeads(); }, []);
  const [leadId, setLeadId] = useState('');
  const [tone, setTone] = useState<AiTone>('friendly');
  const [context, setContext] = useState('');
  const [result, setResult] = useState<GeneratedEmail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const generate = async () => {
    if (!leadId) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await aiApi.generateEmail(leadId, tone, context || undefined));
    } catch {
      setError(t('aiAssistant.errors.email'));
    } finally {
      setLoading(false);
    }
  };

  const copyAll = () => {
    if (!result) return;
    navigator.clipboard.writeText(`${result.subject}\n\n${result.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const TONES: AiTone[] = ['friendly', 'formal', 'assertive'];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
      <Box sx={{ ...card, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          {/* Lead selector */}
          <FormControl size="small" sx={{ flex: '1 1 220px' }}>
            <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('aiAssistant.selectLead')}</InputLabel>
            <Select
              value={leadId}
              label={t('aiAssistant.selectLead')}
              onChange={(e) => { setLeadId(e.target.value); setResult(null); }}
              sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
            >
              <MenuItem value="" disabled sx={{ fontFamily: 'Inter', fontSize: 13, color: '#94A3B8' }}>
                {t('aiAssistant.selectLeadPlaceholder')}
              </MenuItem>
              {leads.map((l) => (
                <MenuItem key={l.id} value={l.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                  {l.first_name} {l.last_name} {l.company ? `— ${l.company}` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Tone selector */}
          <FormControl size="small" sx={{ flex: '0 0 160px' }}>
            <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('aiAssistant.email.tone')}</InputLabel>
            <Select
              value={tone}
              label={t('aiAssistant.email.tone')}
              onChange={(e) => setTone(e.target.value as AiTone)}
              sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
            >
              {TONES.map((tn) => (
                <MenuItem key={tn} value={tn} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                  {t(`aiAssistant.email.tones.${tn}`)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={generate}
            disabled={!leadId || loading}
            sx={{
              bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
              fontSize: 13, borderRadius: '8px', textTransform: 'none', boxShadow: 'none',
              px: 2.5, height: 40, whiteSpace: 'nowrap',
              '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
              '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
            }}
          >
            {loading ? t('aiAssistant.email.generating') : t('aiAssistant.email.generate')}
          </Button>
        </Box>

        {/* Extra context */}
        <TextField
          multiline
          rows={2}
          size="small"
          label={t('aiAssistant.email.context')}
          placeholder={t('aiAssistant.email.contextPlaceholder')}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          sx={{
            '& .MuiInputBase-root': { fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' },
            '& label': { fontFamily: 'Inter', fontSize: 13 },
          }}
        />
      </Box>

      {error && <Alert severity="error" sx={{ borderRadius: '10px' }}>{error}</Alert>}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress sx={{ color: '#00A8E8' }} />
        </Box>
      )}

      {result && !loading && (
        <Box sx={card}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 14, color: '#0D2144' }}>
              {t('aiAssistant.email.subject')}: {result.subject}
            </Typography>
            <Button
              size="small"
              onClick={copyAll}
              sx={{
                fontFamily: 'Inter', fontSize: 12, fontWeight: 600,
                color: copied ? '#059669' : '#00A8E8',
                textTransform: 'none', minWidth: 0,
              }}
            >
              {copied ? t('aiAssistant.email.copied') : t('aiAssistant.email.copy')}
            </Button>
          </Box>
          <Box sx={{
            bgcolor: '#F7F9FC', border: '1px solid #E8EFF7',
            borderRadius: '8px', p: 2,
          }}>
            <Typography sx={{
              fontFamily: 'Inter', fontSize: 13, color: '#334155',
              lineHeight: 1.8, whiteSpace: 'pre-wrap',
            }}>
              {result.body}
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Bullet list helper ──────────────────────────────────────────────────────── */
function BulletList({ items, color = '#00A8E8' }: { items: string[]; color?: string }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
      {items.map((item, i) => (
        <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
          <Box sx={{ mt: 0.6, width: 6, height: 6, borderRadius: '50%', bgcolor: color, flexShrink: 0 }} />
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
            {item}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}

/* ── Lost Deals Analysis Tab ─────────────────────────────────────────────────── */
function LostDealsAnalysisTab() {
  const { t } = useTranslation();
  const [result, setResult] = useState<LostDealsAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await aiApi.analyzeLostDeals());
    } catch {
      setError(t('aiAssistant.errors.lostAnalysis'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
      <Box sx={{ ...card, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', flex: 1 }}>
          {t('aiAssistant.lostAnalysis.description')}
        </Typography>
        <Button
          variant="contained"
          onClick={run}
          disabled={loading}
          sx={{
            bgcolor: '#FF6B35', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '8px', textTransform: 'none', boxShadow: 'none',
            px: 2.5, height: 40, whiteSpace: 'nowrap',
            '&:hover': { bgcolor: '#e05a27', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {loading ? t('aiAssistant.lostAnalysis.running') : t('aiAssistant.lostAnalysis.runButton')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ borderRadius: '10px' }}>{error}</Alert>}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress sx={{ color: '#FF6B35' }} />
        </Box>
      )}

      {result && !loading && (
        <>
          {result.total_deals === 0 ? (
            <Alert severity="info" sx={{ borderRadius: '10px' }}>{t('aiAssistant.lostAnalysis.noDeals')}</Alert>
          ) : (
            <Box sx={{ display: 'flex', gap: 2.5, flexWrap: 'wrap' }}>
              {/* Stats */}
              <Box sx={{ ...card, flex: '1 1 200px', display: 'flex', gap: 3 }}>
                <Box>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase', mb: 0.5 }}>
                    {t('aiAssistant.lostAnalysis.totalDeals')}
                  </Typography>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 28, fontWeight: 800, color: '#FF6B35' }}>
                    {result.total_deals}
                  </Typography>
                </Box>
                <Box>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase', mb: 0.5 }}>
                    {t('aiAssistant.lostAnalysis.totalValue')}
                  </Typography>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 28, fontWeight: 800, color: '#DC2626' }}>
                    ${result.total_lost_value.toLocaleString()}
                  </Typography>
                </Box>
              </Box>

              {/* Summary */}
              <Box sx={{ ...card, flex: '1 1 100%' }}>
                <Typography sx={sectionTitle}>{t('aiAssistant.lostAnalysis.summary')}</Typography>
                <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.7 }}>
                  {result.summary}
                </Typography>
              </Box>

              {/* Loss patterns */}
              <Box sx={{ ...card, flex: '1 1 260px' }}>
                <Typography sx={sectionTitle}>{t('aiAssistant.lostAnalysis.patterns')}</Typography>
                <BulletList items={result.loss_patterns} color="#DC2626" />
              </Box>

              {/* Recommendations */}
              <Box sx={{ ...card, flex: '1 1 260px' }}>
                <Typography sx={sectionTitle}>{t('aiAssistant.lostAnalysis.recommendations')}</Typography>
                <BulletList items={result.recommendations} color="#059669" />
              </Box>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

/* ── Pipeline Digest Tab ─────────────────────────────────────────────────────── */
function PipelineDigestTab() {
  const { t } = useTranslation();
  const allPipelines = useKanbanStore((s) => s.allPipelines);
  const loadPipelines = useKanbanStore((s) => s.loadPipelines);
  useEffect(() => { if (allPipelines.length === 0) loadPipelines(); }, []);

  const [pipelineId, setPipelineId] = useState('');
  const [result, setResult] = useState<PipelineDigest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    if (!pipelineId) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await aiApi.pipelineWeeklyDigest(pipelineId));
    } catch {
      setError(t('aiAssistant.errors.pipelineDigest'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
      <Box sx={{ ...card, display: 'flex', gap: 2, alignItems: 'flex-end' }}>
        <FormControl size="small" sx={{ flex: 1 }}>
          <InputLabel sx={{ fontFamily: 'Inter', fontSize: 13 }}>{t('aiAssistant.digest.selectPipeline')}</InputLabel>
          <Select
            value={pipelineId}
            label={t('aiAssistant.digest.selectPipeline')}
            onChange={(e) => { setPipelineId(e.target.value); setResult(null); }}
            sx={{ fontFamily: 'Inter', fontSize: 13, borderRadius: '8px' }}
          >
            {allPipelines.map((p) => (
              <MenuItem key={p.id} value={p.id} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
                {p.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button
          variant="contained"
          onClick={run}
          disabled={!pipelineId || loading}
          sx={{
            bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
            fontSize: 13, borderRadius: '8px', textTransform: 'none', boxShadow: 'none',
            px: 2.5, height: 40, whiteSpace: 'nowrap',
            '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
          }}
        >
          {loading ? t('aiAssistant.digest.running') : t('aiAssistant.digest.runButton')}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ borderRadius: '10px' }}>{error}</Alert>}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress sx={{ color: '#00A8E8' }} />
        </Box>
      )}

      {result && !loading && (
        <Box sx={{ display: 'flex', gap: 2.5, flexWrap: 'wrap' }}>
          {/* Summary */}
          <Box sx={{ ...card, flex: '1 1 100%' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.digest.summary')}</Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#475569', lineHeight: 1.7 }}>
              {result.summary}
            </Typography>
          </Box>

          {/* Key metrics */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={{ ...sectionTitle, mb: 1.5 }}>{t('aiAssistant.digest.keyMetrics')}</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {result.key_metrics.map((m, i) => (
                <Chip
                  key={i}
                  label={m}
                  size="small"
                  sx={{
                    fontFamily: 'Inter', fontSize: 12, fontWeight: 500,
                    bgcolor: 'rgba(0,168,232,0.1)', color: '#00A8E8',
                    border: '1px solid rgba(0,168,232,0.2)',
                  }}
                />
              ))}
            </Box>
          </Box>

          {/* Risks */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.digest.risks')}</Typography>
            <BulletList items={result.risks} color="#DC2626" />
          </Box>

          {/* Opportunities */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.digest.opportunities')}</Typography>
            <BulletList items={result.opportunities} color="#059669" />
          </Box>

          {/* Focus deals */}
          <Box sx={{ ...card, flex: '1 1 260px' }}>
            <Typography sx={sectionTitle}>{t('aiAssistant.digest.focusDeals')}</Typography>
            <BulletList items={result.focus_deals} color="#F59E0B" />
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Main page ──────────────────────────────────────────────────────────────── */
export default function AIAssistantPage() {
  const { t } = useTranslation();
  const [tab, setTab] = useState(0);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5 }}>
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144' }}>
            {t('aiAssistant.title')}
          </Typography>
          {/* Pulsing AI dot */}
          <Box sx={{
            width: 8, height: 8, borderRadius: '50%', bgcolor: '#00A8E8',
            animation: 'pulse 2s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1, transform: 'scale(1)' },
              '50%': { opacity: 0.5, transform: 'scale(0.85)' },
            },
          }} />
          <Box sx={{
            display: 'inline-flex', px: 1.25, py: 0.3,
            bgcolor: 'rgba(0,168,232,0.1)', borderRadius: '20px',
            color: '#00A8E8', fontFamily: 'Inter', fontSize: 11, fontWeight: 700,
          }}>
            GPT-4
          </Box>
        </Box>
        <Typography sx={{ fontFamily: 'Inter, sans-serif', fontSize: 14, color: '#64748B' }}>
          {t('aiAssistant.subtitle')}
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{
        background: '#FFFFFF', border: '1px solid #E8EFF7',
        borderRadius: '12px', boxShadow: '0 1px 4px rgba(13,33,68,0.06)',
        mb: 2.5,
      }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{
            px: 2,
            '& .MuiTab-root': {
              fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 500,
              textTransform: 'none', color: '#64748B', minHeight: 48,
            },
            '& .Mui-selected': { color: '#00A8E8 !important', fontWeight: 600 },
            '& .MuiTabs-indicator': { bgcolor: '#00A8E8', height: 2.5, borderRadius: '2px 2px 0 0' },
          }}
        >
          <Tab label={t('aiAssistant.tabs.leadScore')} />
          <Tab label={t('aiAssistant.tabs.dealForecast')} />
          <Tab label={t('aiAssistant.tabs.emailGen')} />
          <Tab label={t('aiAssistant.tabs.lostAnalysis')} />
          <Tab label={t('aiAssistant.tabs.pipelineDigest')} />
        </Tabs>
      </Box>

      {/* Tab panels */}
      {tab === 0 && <LeadScoreTab />}
      {tab === 1 && <DealForecastTab />}
      {tab === 2 && <EmailGenTab />}
      {tab === 3 && <LostDealsAnalysisTab />}
      {tab === 4 && <PipelineDigestTab />}
    </Box>
  );
}
