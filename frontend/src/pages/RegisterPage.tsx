import { Alert, Box, Button, CircularProgress, Divider, Typography } from '@mui/material';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { getMe, login, register } from '../api/auth';
import AuthLayout, { inputSx } from '../components/auth/AuthLayout';
import { useAuthStore } from '../store/useAuthStore';

export default function RegisterPage() {
  const navigate = useNavigate();
  const setAuth  = useAuthStore((s) => s.setAuth);
  const { t }    = useTranslation();

  const [name,     setName]     = useState('');
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [confirm,  setConfirm]  = useState('');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password !== confirm) { setError(t('auth.passwordMismatch')); return; }

    const parts      = name.trim().split(/\s+/);
    const first_name = parts[0] ?? name.trim();
    const last_name  = parts.slice(1).join(' ') || first_name;

    setLoading(true);
    try {
      await register({ first_name, last_name, email, password });
      const tokenData = await login({ email, password });
      localStorage.setItem('crm-auth', JSON.stringify({ state: { token: tokenData.access_token } }));
      const user = await getMe();
      setAuth(tokenData.access_token, user);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout activeTab="register">

      <Box sx={{ mb: 3 }}>
        <Typography sx={{
          fontSize: 26, fontWeight: 700, color: '#171C20',
          fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em', lineHeight: 1.2,
        }}>
          {t('auth.createAccount')}
        </Typography>
        <Typography sx={{ fontSize: 14, color: '#6E7881', fontFamily: 'Inter, sans-serif', mt: 0.75 }}>
          {t('auth.createSubtitle')}
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, fontSize: 13 }}>{error}</Alert>}

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {[
          { label: t('auth.fullName'),        value: name,     onChange: setName,     type: 'text',     placeholder: t('auth.fullNamePlaceholder'), hint: '',                         autoFocus: true  },
          { label: t('auth.workEmail'),        value: email,    onChange: setEmail,    type: 'email',    placeholder: t('auth.emailPlaceholder'),    hint: '',                         autoFocus: false },
          { label: t('auth.password'),         value: password, onChange: setPassword, type: 'password', placeholder: t('auth.passwordPlaceholder'), hint: t('auth.passwordHint'),     autoFocus: false },
          { label: t('auth.confirmPassword'),  value: confirm,  onChange: setConfirm,  type: 'password', placeholder: t('auth.passwordPlaceholder'), hint: '',                         autoFocus: false },
        ].map(({ label, value, onChange, type, placeholder, hint, autoFocus }) => (
          <Box key={label}>
            <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', mb: '6px', fontFamily: 'Inter, sans-serif' }}>
              {label}
            </Typography>
            <Box
              component="input"
              type={type}
              required
              autoFocus={autoFocus}
              placeholder={placeholder}
              value={value}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
              sx={inputSx}
            />
            {hint && (
              <Typography sx={{ fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif', mt: '4px' }}>
                {hint}
              </Typography>
            )}
          </Box>
        ))}

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
          {loading ? <CircularProgress size={20} color="inherit" /> : t('auth.registerButton')}
        </Button>
      </Box>

      {/* Divider */}
      <Box sx={{ position: 'relative', my: 3 }}>
        <Divider sx={{ borderColor: '#D6DAE0' }} />
        <Box sx={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)',
          bgcolor: 'background.paper', px: 1.5,
          fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif',
          whiteSpace: 'nowrap',
        }}>
          {t('auth.orContinueWith')}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {[
          { key: 'google',    icon: 'G' },
          { key: 'magicLink', icon: '✉' },
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
              color: 'text.primary',
              fontSize: 14, fontWeight: 700, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer',
              transition: 'background 0.15s',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            {icon}&nbsp;{t(`auth.${key}`)}
          </Box>
        ))}
      </Box>

      <Typography sx={{ mt: 3, textAlign: 'center', fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif' }}>
        {t('auth.termsByCreating')}{' '}
        <Box component="a" href="#" sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          {t('auth.termsLink')}
        </Box>{' '}
        {t('auth.and')}{' '}
        <Box component="a" href="#" sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          {t('auth.privacyLink')}
        </Box>.
      </Typography>

    </AuthLayout>
  );
}
