import { Alert, Box, Button, CircularProgress, Divider, Link, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { getMe, login } from '../api/auth';
import AuthLayout, { inputSx } from '../components/auth/AuthLayout';
import { useAuthStore } from '../store/useAuthStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth  = useAuthStore((s) => s.setAuth);
  const { t }    = useTranslation();

  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokenData = await login({ email, password });
      // Temporarily store token so getMe() interceptor can attach it
      localStorage.setItem('crm-auth', JSON.stringify({
        state: { token: tokenData.access_token, refreshToken: tokenData.refresh_token },
      }));
      const user = await getMe();
      setAuth(tokenData.access_token, user, tokenData.refresh_token);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout activeTab="login">

      {error && <Alert severity="error" sx={{ mb: 2.5, fontSize: 13 }}>{error}</Alert>}

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
        {/* Email */}
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

        {/* Password */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: '6px' }}>
            <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', fontFamily: 'Inter, sans-serif' }}>
              {t('auth.password')}
            </Typography>
            <Link
              component={RouterLink}
              to="/forgot-password"
              sx={{ fontSize: 12, color: '#00A8E8', textDecoration: 'none', fontFamily: 'Inter, sans-serif', '&:hover': { textDecoration: 'underline' } }}
            >
              {t('auth.forgotPassword')}
            </Link>
          </Box>
          <Box
            component="input"
            type="password"
            required
            placeholder={t('auth.passwordPlaceholder')}
            value={password}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            sx={inputSx}
          />
        </Box>

        {/* Submit */}
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
          {loading ? <CircularProgress size={20} color="inherit" /> : t('auth.signInButton')}
        </Button>
      </Box>

      {/* Divider */}
      <Box sx={{ position: 'relative', my: 3 }}>
        <Divider sx={{ borderColor: '#D6DAE0' }} />
        <Box sx={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)',
          bgcolor: '#fff', px: 1.5,
          fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif',
          whiteSpace: 'nowrap',
        }}>
          {t('auth.orContinueWith')}
        </Box>
      </Box>

      {/* Alternative login */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {[
          { key: 'magicLink', icon: '✉' },
          { key: 'google',    icon: 'G' },
        ].map(({ key, icon }) => (
          <Box
            key={key}
            component="button"
            type="button"
            sx={{
              height: 44,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1,
              border: '1px solid #0D2144',
              borderRadius: '8px',
              bgcolor: 'transparent',
              color: '#0D2144',
              fontSize: 14, fontWeight: 700, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer',
              transition: 'background 0.15s',
              '&:hover': { bgcolor: '#F0F5FF' },
            }}
          >
            {icon}&nbsp;{t(`auth.${key}`)}
          </Box>
        ))}
      </Box>

      {/* Legal */}
      <Typography sx={{ mt: 3, textAlign: 'center', fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif' }}>
        {t('auth.terms')}{' '}
        <Link sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          {t('auth.termsLink')}
        </Link>{' '}
        {t('auth.and')}{' '}
        <Link sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          {t('auth.privacyLink')}
        </Link>.
      </Typography>

    </AuthLayout>
  );
}
