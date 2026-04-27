import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { type AiTone, type GeneratedEmail, type LeadScore, type NextBestAction } from '../../types/ai';

// ── Score gauge ─────────────────────────────────────────────────────────────────

function scoreColor(score: number): 'success' | 'warning' | 'error' {
  if (score >= 0.7) return 'success';
  if (score >= 0.4) return 'warning';
  return 'error';
}

interface ScoreSectionProps {
  score: LeadScore | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

function ScoreSection({ score, loading, error, onRefresh }: ScoreSectionProps) {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" fontWeight={700}>
          ИИ-оценка лида
        </Typography>
        <Button size="small" onClick={onRefresh} disabled={loading} startIcon={<AutoAwesomeIcon />}>
          {score ? 'Обновить' : 'Оценить'}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 1 }} />}
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      {score && (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={score.score * 100}
                color={scoreColor(score.score)}
                size={64}
                thickness={5}
              />
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="caption" fontWeight={700}>
                  {Math.round(score.score * 100)}%
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {score.reasoning}
            </Typography>
          </Box>

          {score.recommended_actions.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                Рекомендованные действия
              </Typography>
              <List dense disablePadding>
                {score.recommended_actions.map((action, i) => (
                  <ListItem key={i} disablePadding sx={{ py: 0.25 }}>
                    <ListItemText
                      primary={action}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}

// ── Next Best Action ────────────────────────────────────────────────────────────

const PRIORITY_COLOR: Record<NextBestAction['priority'], 'error' | 'warning' | 'default'> = {
  high: 'error',
  medium: 'warning',
  low: 'default',
};

interface NextActionSectionProps {
  nextAction: NextBestAction | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

function NextActionSection({ nextAction, loading, error, onRefresh }: NextActionSectionProps) {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" fontWeight={700}>
          Следующий шаг
        </Typography>
        <Button size="small" onClick={onRefresh} disabled={loading} startIcon={<AutoAwesomeIcon />}>
          {nextAction ? 'Обновить' : 'Предложить'}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 1 }} />}
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      {nextAction && (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.75 }}>
            <Chip
              label={nextAction.priority}
              color={PRIORITY_COLOR[nextAction.priority]}
              size="small"
            />
            <Typography variant="body2" fontWeight={600}>
              {nextAction.action}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {nextAction.reasoning}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

// ── Email Generator ─────────────────────────────────────────────────────────────

interface EmailSectionProps {
  generatedEmail: GeneratedEmail | null;
  loading: boolean;
  error: string | null;
  onGenerate: (tone: AiTone, context: string) => void;
}

function EmailSection({ generatedEmail, loading, error, onGenerate }: EmailSectionProps) {
  const [tone, setTone] = useState<AiTone>('friendly');
  const [context, setContext] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!generatedEmail) return;
    const text = `Subject: ${generatedEmail.subject}\n\n${generatedEmail.body}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={700} mb={1}>
        ИИ генератор писем
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <FormControl size="small" sx={{ minWidth: 130 }}>
          <InputLabel>Тон</InputLabel>
          <Select<AiTone>
            value={tone}
            label="Тон"
            onChange={(e) => setTone(e.target.value as AiTone)}
          >
            <MenuItem value="friendly">Дружелюбный</MenuItem>
            <MenuItem value="formal">Официальный</MenuItem>
            <MenuItem value="assertive">Настойчивый</MenuItem>
          </Select>
        </FormControl>
        <TextField
          size="small"
          fullWidth
          placeholder="Доп. контекст (необязательно)"
          value={context}
          onChange={(e) => setContext(e.target.value)}
        />
      </Box>

      <Button
        variant="contained"
        size="small"
        onClick={() => onGenerate(tone, context)}
        disabled={loading}
        startIcon={loading ? <CircularProgress size={14} color="inherit" /> : <AutoAwesomeIcon />}
        sx={{ mb: 1 }}
      >
        {loading ? 'Генерирую…' : 'Сгенерировать'}
      </Button>

      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      {generatedEmail && (
        <Box
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            p: 1.5,
            position: 'relative',
          }}
        >
          <Tooltip title={copied ? 'Скопировано!' : 'Копировать'}>
            <Button
              size="small"
              sx={{ position: 'absolute', top: 8, right: 8 }}
              onClick={handleCopy}
              startIcon={<ContentCopyIcon fontSize="small" />}
            >
              {copied ? 'Скопировано' : 'Копировать'}
            </Button>
          </Tooltip>

          <Typography variant="caption" color="text.secondary" display="block">
            Тема
          </Typography>
          <Typography variant="body2" fontWeight={600} mb={1}>
            {generatedEmail.subject}
          </Typography>

          <Typography variant="caption" color="text.secondary" display="block">
            Текст
          </Typography>
          <Typography
            variant="body2"
            sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 12 }}
          >
            {generatedEmail.body}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

// ── AIBlock (composed) ──────────────────────────────────────────────────────────

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
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          ИИ-инсайты
        </Typography>

        <ScoreSection
          score={score}
          loading={scoreLoading}
          error={scoreError}
          onRefresh={onScoreRefresh}
        />

        <Divider sx={{ my: 2 }} />

        <NextActionSection
          nextAction={nextAction}
          loading={nextActionLoading}
          error={nextActionError}
          onRefresh={onNextActionRefresh}
        />

        <Divider sx={{ my: 2 }} />

        <EmailSection
          generatedEmail={generatedEmail}
          loading={emailLoading}
          error={emailError}
          onGenerate={onGenerateEmail}
        />
      </CardContent>
    </Card>
  );
}
