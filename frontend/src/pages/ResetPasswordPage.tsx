import { Alert, Box, Button, CircularProgress, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../api/auth';
import AuthLayout, { inputSx } from '../components/auth/AuthLayout';

export default function ResetPasswordPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError(t('auth.passwordsMismatch'));
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await resetPassword({ token, new_password: password });
      setDone(true);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error';
      // Map backend Russian message to i18n key
      setError(
        msg.includes('недействителен') || msg.includes('invalid') || msg.includes('expired')
          ? t('auth.invalidResetToken')
          : msg,
      );
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <AuthLayout activeTab="reset">
        <Alert severity="error">{t('auth.invalidResetToken')}</Alert>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout activeTab="reset">
      {done ? (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Box sx={{
            width: 56, height: 56, borderRadius: '50%',
            bgcolor: 'rgba(16,185,129,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            mx: 'auto', mb: 2.5,
          }}>
            <Box component="span" sx={{ fontSize: 26 }}>✓</Box>
          </Box>
          <Typography sx={{ fontSize: 18, fontWeight: 700, color: '#171C20', fontFamily: 'Inter, sans-serif', mb: 1 }}>
            {t('auth.passwordResetSuccess')}
          </Typography>
          <Typography sx={{ fontSize: 13, color: '#6E7881', fontFamily: 'Inter, sans-serif', lineHeight: 1.6, mb: 3 }}>
            {t('auth.passwordResetSuccessMsg')}
          </Typography>
          <Button
            fullWidth
            onClick={() => navigate('/login', { replace: true })}
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
              '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
            }}
          >
            {t('auth.signIn')}
          </Button>
        </Box>
      ) : (
        <>
          <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#171C20', fontFamily: 'Inter, sans-serif', mb: 0.5 }}>
            {t('auth.resetPasswordTitle')}
          </Typography>
          <Typography sx={{ fontSize: 13, color: '#6E7881', fontFamily: 'Inter, sans-serif', mb: 3, lineHeight: 1.5 }}>
            {t('auth.resetPasswordSubtitle')}
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2.5, fontSize: 13 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            <Box>
              <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', mb: '6px', fontFamily: 'Inter, sans-serif' }}>
                {t('auth.newPassword')}
              </Typography>
              <Box
                component="input"
                type="password"
                required
                autoFocus
                minLength={6}
                placeholder={t('auth.newPasswordPlaceholder')}
                value={password}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                sx={inputSx}
              />
            </Box>

            <Box>
              <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', mb: '6px', fontFamily: 'Inter, sans-serif' }}>
                {t('auth.confirmNewPassword')}
              </Typography>
              <Box
                component="input"
                type="password"
                required
                minLength={6}
                placeholder={t('auth.confirmNewPasswordPlaceholder')}
                value={confirm}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirm(e.target.value)}
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
              {loading ? <CircularProgress size={20} color="inherit" /> : t('auth.resetPasswordButton')}
            </Button>
          </Box>
        </>
      )}
    </AuthLayout>
  );
}
