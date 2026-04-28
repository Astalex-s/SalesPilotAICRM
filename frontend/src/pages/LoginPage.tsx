import { Alert, Box, Button, CircularProgress, Divider, Link, Typography } from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, login } from '../api/auth';
import AuthLayout, { inputSx } from '../components/auth/AuthLayout';
import { useAuthStore } from '../store/useAuthStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokenData = await login({ email, password });
      localStorage.setItem('crm-auth', JSON.stringify({ state: { token: tokenData.access_token } }));
      const user = await getMe();
      setAuth(tokenData.access_token, user);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка входа');
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
            Email
          </Typography>
          <Box
            component="input"
            type="email"
            required
            autoFocus
            placeholder="name@company.com"
            value={email}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            sx={inputSx}
          />
        </Box>

        {/* Password */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: '6px' }}>
            <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#171C20', fontFamily: 'Inter, sans-serif' }}>
              Password
            </Typography>
            <Link
              component="button"
              type="button"
              sx={{ fontSize: 12, color: '#00A8E8', textDecoration: 'none', fontFamily: 'Inter, sans-serif', '&:hover': { textDecoration: 'underline' } }}
            >
              Forgot?
            </Link>
          </Box>
          <Box
            component="input"
            type="password"
            required
            placeholder="••••••••"
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
          {loading ? <CircularProgress size={20} color="inherit" /> : 'Sign In'}
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
          Or continue with
        </Box>
      </Box>

      {/* Alternative login */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {[
          { label: 'Magic Link', icon: '✉' },
          { label: 'Google',     icon: 'G' },
        ].map(({ label, icon }) => (
          <Box
            key={label}
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
            {icon}&nbsp;{label}
          </Box>
        ))}
      </Box>

      {/* Legal */}
      <Typography sx={{ mt: 3, textAlign: 'center', fontSize: 12, color: '#6E7881', fontFamily: 'Inter, sans-serif' }}>
        By signing in, you agree to our{' '}
        <Link sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          Terms of Service
        </Link>{' '}
        and{' '}
        <Link sx={{ color: '#00A8E8', fontSize: 12, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          Privacy Policy
        </Link>.
      </Typography>

    </AuthLayout>
  );
}
