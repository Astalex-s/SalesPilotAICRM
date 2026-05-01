import { Alert, Box, Button, CircularProgress, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { forgotPassword } from '../api/auth';
import AuthLayout, { inputSx } from '../components/auth/AuthLayout';

export default function ForgotPasswordPage() {
  const { t } = useTranslation();

  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await forgotPassword({ email });
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout activeTab="forgot">
      {sent ? (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Box sx={{
            width: 56, height: 56, borderRadius: '50%',
            bgcolor: 'rgba(0,168,232,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            mx: 'auto', mb: 2.5,
          }}>
            <Box component="span" sx={{ fontSize: 26 }}>✉</Box>
          </Box>
          <Typography sx={{ fontSize: 18, fontWeight: 700, color: '#171C20', fontFamily: 'Inter, sans-serif', mb: 1 }}>
            {t('auth.checkYourEmail')}
          </Typography>
          <Typography sx={{ fontSize: 13, color: '#6E7881', fontFamily: 'Inter, sans-serif', lineHeight: 1.6 }}>
            {t('auth.resetLinkSent')}
          </Typography>
        </Box>
      ) : (
        <>
          <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#171C20', fontFamily: 'Inter, sans-serif', mb: 0.5 }}>
            {t('auth.forgotPasswordTitle')}
          </Typography>
          <Typography sx={{ fontSize: 13, color: '#6E7881', fontFamily: 'Inter, sans-serif', mb: 3, lineHeight: 1.5 }}>
            {t('auth.forgotPasswordSubtitle')}
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2.5, fontSize: 13 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            <Box>
              <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', mb: '6px', fontFamily: 'Inter, sans-serif' }}>
                {t('auth.email')}
              </Typography>
              <Box
                component="input"
                type="email"
                required
                autoFocus
                placeholder={t('auth.emailPlaceholder')}
                value={email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                sx={inputSx}
              />
            </Box>

            <Button
              type="submit"
              fullWidth
              disabled={loading}
              sx={{
                height: 44,
                bgcolor: '#00A8E8',
                color: '#fff',
                fontWeight: 700,
                fontSize: 14,
                fontFamily: 'Inter, sans-serif',
                borderRadius: '8px',
                textTransform: 'none',
                boxShadow: 'none',
                mt: 0.5,
                '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
                '&.Mui-disabled': { bgcolor: '#BDC8D1', color: '#fff' },
              }}
            >
              {loading ? <CircularProgress size={20} color="inherit" /> : t('auth.sendResetLink')}
            </Button>
          </Box>
        </>
      )}
    </AuthLayout>
  );
}
