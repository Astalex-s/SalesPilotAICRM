import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import RefreshIcon from '@mui/icons-material/Refresh';
import {
  Alert,
  Box,
  Button,
  Card,
  CircularProgress,
  Divider,
  LinearProgress,
  MenuItem,
  Select,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { type AiTone, type GeneratedEmail, type LeadScore, type NextBestAction } from '../../types/ai';

/* ── Design tokens ── */
const CARD_STYLE = {
  bgcolor: 'background.paper',
  border: '1px solid', borderColor: 'divider',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
  height: '100%',
};

const SECTION_LABEL_SX = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 11,
  fontWeight: 500,
  letterSpacing: '0.07em',
  textTransform: 'uppercase' as const,
  color: '#94A3B8',
  mb: 1,
};

const INPUT_SX = {
  '& .MuiOutlinedInput-root': {
    borderRadius: '10px',
    fontFamily: 'Inter, sans-serif',
    fontSize: 13,
    '& fieldset': { borderColor: 'divider' },
    '&:hover fieldset': { borderColor: '#CBD5E8' },
    '&.Mui-focused fieldset': { borderColor: '#00A8E8', borderWidth: 2 },
  },
};

const CYAN_BTN_SX = {
  fontFamily: 'Inter, sans-serif',
  fontWeight: 600,
  fontSize: 13,
  bgcolor: '#00A8E8',
  color: '#fff',
  borderRadius: '8px',
  textTransform: 'none' as const,
  boxShadow: 'none',
  '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
  '&.Mui-disabled': { bgcolor: '#E2EAF4', color: '#94A3B8' },
};

function scoreColor(score: number): string {
  if (score >= 0.7) return '#10B981';
  if (score >= 0.4) return '#F59E0B';
  return '#EF4444';
}

/* ── Score Section ── */
interface ScoreSectionProps {
  score: LeadScore | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

function ScoreSection({ score, loading, error, onRefresh }: ScoreSectionProps) {
  const { t } = useTranslation();
  const pct = score ? Math.round(score.score * 100) : 0;
  const color = score ? scoreColor(score.score) : '#94A3B8';

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
        <Typography sx={SECTION_LABEL_SX}>{t('leadDetail.ai.score')}</Typography>
        <Button
          size="small"
          onClick={onRefresh}
          disabled={loading}
          startIcon={<RefreshIcon sx={{ fontSize: 14 }} />}
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 600,
            color: '#00A8E8',
            textTransform: 'none',
            minWidth: 0,
            p: '2px 8px',
            '&:hover': { bgcolor: '#E8F4FF' },
          }}
        >
          {score ? t('leadDetail.ai.refresh') : t('leadDetail.ai.scoreBtn')}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 1.5, borderRadius: 2, bgcolor: 'action.hover', '& .MuiLinearProgress-bar': { bgcolor: '#00A8E8' } }} />}
      {error && <Alert severity="error" sx={{ mb: 1.5, borderRadius: '10px', py: 0.5 }}>{error}</Alert>}

      {score && (
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          {/* Circular score */}
          <Box sx={{ position: 'relative', display: 'inline-flex', flexShrink: 0 }}>
            <CircularProgress
              variant="determinate"
              value={pct}
              size={56}
              thickness={5}
              sx={{ color }}
            />
            <CircularProgress
              variant="determinate"
              value={100}
              size={56}
              thickness={5}
              sx={{ color: '#F0F5FF', position: 'absolute', top: 0, left: 0 }}
            />
            <Box sx={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 700, color }}>
                {pct}%
              </Typography>
            </Box>
          </Box>

          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: 'text.secondary', lineHeight: 1.5, mb: 1 }}>
              {score.reasoning}
            </Typography>
            {score.recommended_actions.length > 0 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                {score.recommended_actions.map((action, i) => (
                  <Box key={i} sx={{ display: 'flex', gap: 0.75, alignItems: 'flex-start' }}>
                    <Box sx={{ width: 4, height: 4, borderRadius: '50%', bgcolor: '#00A8E8', mt: '6px', flexShrink: 0 }} />
                    <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: 'text.secondary', lineHeight: 1.5 }}>
                      {action}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
}

/* ── Next Action Section ── */
const PRIORITY_STYLE: Record<NextBestAction['priority'], { bg: string; color: string }> = {
  high:   { bg: 'rgba(239,68,68,0.12)',  color: '#DC2626' },
  medium: { bg: 'rgba(245,158,11,0.12)', color: '#D97706' },
  low:    { bg: 'rgba(148,163,184,0.12)', color: '#64748B' },
};

interface NextActionSectionProps {
  nextAction: NextBestAction | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

function NextActionSection({ nextAction, loading, error, onRefresh }: NextActionSectionProps) {
  const { t } = useTranslation();

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
        <Typography sx={SECTION_LABEL_SX}>{t('leadDetail.ai.actions')}</Typography>
        <Button
          size="small"
          onClick={onRefresh}
          disabled={loading}
          startIcon={<RefreshIcon sx={{ fontSize: 14 }} />}
          sx={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 600,
            color: '#00A8E8',
            textTransform: 'none',
            minWidth: 0,
            p: '2px 8px',
            '&:hover': { bgcolor: '#E8F4FF' },
          }}
        >
          {nextAction ? t('leadDetail.ai.refresh') : t('leadDetail.ai.actionsBtn')}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 1.5, borderRadius: 2, bgcolor: 'action.hover', '& .MuiLinearProgress-bar': { bgcolor: '#00A8E8' } }} />}
      {error && <Alert severity="error" sx={{ mb: 1.5, borderRadius: '10px', py: 0.5 }}>{error}</Alert>}

      {nextAction && (
        <Box
          sx={{
            p: 1.5,
            borderRadius: '10px',
            bgcolor: 'background.default',
            border: '1px solid', borderColor: 'divider',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.75 }}>
            <Box
              sx={{
                px: 1,
                py: 0.2,
                borderRadius: '20px',
                bgcolor: PRIORITY_STYLE[nextAction.priority].bg,
                color: PRIORITY_STYLE[nextAction.priority].color,
                fontFamily: 'Inter',
                fontSize: 11,
                fontWeight: 600,
              }}
            >
              {t(`leadDetail.ai.priority.${nextAction.priority}`)}
            </Box>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: 'text.primary' }}>
              {nextAction.action}
            </Typography>
          </Box>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8', lineHeight: 1.5 }}>
            {nextAction.reasoning}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

/* ── Email Generator ── */
const TONES: AiTone[] = ['friendly', 'formal', 'assertive'];

interface EmailSectionProps {
  generatedEmail: GeneratedEmail | null;
  loading: boolean;
  error: string | null;
  onGenerate: (tone: AiTone, context: string) => void;
}

function EmailSection({ generatedEmail, loading, error, onGenerate }: EmailSectionProps) {
  const { t } = useTranslation();
  const [tone, setTone] = useState<AiTone>('friendly');
  const [context, setContext] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!generatedEmail) return;
    navigator.clipboard.writeText(`Subject: ${generatedEmail.subject}\n\n${generatedEmail.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box>
      <Typography sx={{ ...SECTION_LABEL_SX, mb: 1.5 }}>{t('leadDetail.ai.emailGen')}</Typography>

      {/* Tone + context */}
      <Box sx={{ display: 'flex', gap: 1, mb: 1.5 }}>
        <Select
          value={tone}
          onChange={(e) => setTone(e.target.value as AiTone)}
          size="small"
          sx={{
            minWidth: 110,
            borderRadius: '10px',
            fontFamily: 'Inter',
            fontSize: 13,
            '& .MuiOutlinedInput-notchedOutline': { borderColor: 'divider' },
            '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#CBD5E8' },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00A8E8', borderWidth: 2 },
          }}
        >
          {TONES.map((tn) => (
            <MenuItem key={tn} value={tn} sx={{ fontFamily: 'Inter', fontSize: 13 }}>
              {t(`leadDetail.ai.tones.${tn}`)}
            </MenuItem>
          ))}
        </Select>
        <TextField
          size="small"
          fullWidth
          placeholder={t('leadDetail.ai.emailContext')}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          sx={INPUT_SX}
        />
      </Box>

      <Button
        variant="contained"
        size="small"
        onClick={() => onGenerate(tone, context)}
        disabled={loading}
        startIcon={loading ? <CircularProgress size={13} color="inherit" /> : <AutoAwesomeIcon sx={{ fontSize: 14 }} />}
        sx={{ ...CYAN_BTN_SX, mb: 1.5, px: 2 }}
      >
        {loading ? t('leadDetail.ai.emailGenerating') : t('leadDetail.ai.emailGenBtn')}
      </Button>

      {error && <Alert severity="error" sx={{ mb: 1.5, borderRadius: '10px', py: 0.5 }}>{error}</Alert>}

      {generatedEmail && (
        <Box
          sx={{
            border: '1px solid', borderColor: 'divider',
            borderRadius: '10px',
            p: 1.5,
            bgcolor: 'background.default',
            position: 'relative',
          }}
        >
          <Tooltip title={copied ? t('leadDetail.ai.copied') : t('leadDetail.ai.copy')}>
            <Button
              size="small"
              onClick={handleCopy}
              startIcon={<ContentCopyIcon sx={{ fontSize: 13 }} />}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                fontFamily: 'Inter',
                fontSize: 12,
                textTransform: 'none',
                color: '#00A8E8',
                fontWeight: 600,
                '&:hover': { bgcolor: '#E8F4FF' },
              }}
            >
              {copied ? t('leadDetail.ai.copied') : t('leadDetail.ai.copy')}
            </Button>
          </Tooltip>

          <Typography sx={{ ...SECTION_LABEL_SX, mb: 0.5 }}>{t('leadDetail.ai.emailSubject')}</Typography>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: 'text.primary', mb: 1.5 }}>
            {generatedEmail.subject}
          </Typography>

          <Typography sx={{ ...SECTION_LABEL_SX, mb: 0.5 }}>{t('leadDetail.ai.emailBody')}</Typography>
          <Typography sx={{ fontFamily: 'monospace', fontSize: 12, color: 'text.secondary', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
            {generatedEmail.body}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

/* ── AIBlock ── */
interface AIBlockProps {
  score: LeadScore | null;
  scoreLoading: boolean;
  scoreError: string | null;
  nextAction: NextBestAction | null;
  nextActionLoading: boolean;
  nextActionError: string | null;
  generatedEmail: GeneratedEmail | null;
  emailLoading: boolean;
  emailError: string | null;
  onScoreRefresh: () => void;
  onNextActionRefresh: () => void;
  onGenerateEmail: (tone: AiTone, context: string) => void;
}

export default function AIBlock({
  score, scoreLoading, scoreError,
  nextAction, nextActionLoading, nextActionError,
  generatedEmail, emailLoading, emailError,
  onScoreRefresh, onNextActionRefresh, onGenerateEmail,
}: AIBlockProps) {
  const { t } = useTranslation();

  return (
    <Card elevation={0} sx={CARD_STYLE}>
      <Box sx={{ p: 2.5 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
          <AutoAwesomeIcon sx={{ color: '#00A8E8', fontSize: 18 }} />
          <Typography sx={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 15, color: 'text.primary' }}>
            {t('leadDetail.ai.title')}
          </Typography>
          <Box
            sx={{
              ml: 'auto',
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              px: 1,
              py: 0.3,
              borderRadius: '20px',
              bgcolor: 'rgba(16,185,129,0.1)',
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: '#10B981',
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.4 },
                },
              }}
            />
            <Typography sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 600, color: '#059669' }}>
              {t('leadDetail.ai.live')}
            </Typography>
          </Box>
        </Box>

        <ScoreSection
          score={score}
          loading={scoreLoading}
          error={scoreError}
          onRefresh={onScoreRefresh}
        />

        <Divider sx={{ borderColor: '#F0F5FF', my: 2 }} />

        <NextActionSection
          nextAction={nextAction}
          loading={nextActionLoading}
          error={nextActionError}
          onRefresh={onNextActionRefresh}
        />

        <Divider sx={{ borderColor: '#F0F5FF', my: 2 }} />

        <EmailSection
          generatedEmail={generatedEmail}
          loading={emailLoading}
          error={emailError}
          onGenerate={onGenerateEmail}
        />
      </Box>
    </Card>
  );
}
