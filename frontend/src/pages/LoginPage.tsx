import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Link,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, login } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';

/* ── Wave background (shared with RegisterPage) ──────────────────────────────── */
const WaveBg = () => (
  <svg
    viewBox="0 0 900 600"
    xmlns="http://www.w3.org/2000/svg"
    style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
    preserveAspectRatio="xMidYMid slice"
  >
    <defs>
      <linearGradient id="waveBlue1" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stopColor="#5BC8F5" stopOpacity="0.7" />
        <stop offset="100%" stopColor="#3A9ED8" stopOpacity="0.4" />
      </linearGradient>
      <linearGradient id="waveBlue2" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stopColor="#7DD8FA" stopOpacity="0.55" />
        <stop offset="100%" stopColor="#4AB8F0" stopOpacity="0.3" />
      </linearGradient>
      <linearGradient id="wavePink" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stopColor="#F5A8C8" stopOpacity="0.65" />
        <stop offset="100%" stopColor="#E890B8" stopOpacity="0.3" />
      </linearGradient>
      <linearGradient id="waveCyan" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stopColor="#A0E8FA" stopOpacity="0.5" />
        <stop offset="100%" stopColor="#70C8F0" stopOpacity="0.2" />
      </linearGradient>
      <linearGradient id="barGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%"   stopColor="#5BB8F5" stopOpacity="0.55" />
        <stop offset="100%" stopColor="#A070D8" stopOpacity="0.3" />
      </linearGradient>
      <linearGradient id="barPink" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%"   stopColor="#F090C0" stopOpacity="0.55" />
        <stop offset="100%" stopColor="#C060A0" stopOpacity="0.25" />
      </linearGradient>
    </defs>
    <rect width="900" height="600" fill="#F5F9FD" />
    <path d="M-20 430 C80 340,220 500,380 400 C540 300,640 460,780 350 C840 310,880 320,920 310 L920 640 L-20 640 Z" fill="url(#waveBlue1)" />
    <path d="M-20 470 C60 380,180 520,340 430 C500 340,620 490,780 390 C840 355,880 360,920 350 L920 640 L-20 640 Z" fill="url(#waveCyan)" />
    <path d="M-20 390 C100 280,260 440,420 360 C580 280,680 420,820 330 C860 308,900 315,920 310 L920 640 L-20 640 Z" fill="url(#wavePink)" />
    <path d="M-20 360 C120 240,280 410,440 330 C600 250,700 390,860 300 L920 640 L-20 640 Z" fill="url(#waveBlue2)" />
    <path d="M-20 0 C150 60,300 20,500 80 C650 130,750 60,920 100 L920 0 Z" fill="#B8E8FA" opacity="0.3" />
    <rect x="330" y="210" width="36" height="180" rx="5" fill="url(#barGrad)" />
    <rect x="376" y="160" width="36" height="230" rx="5" fill="url(#barPink)"  />
    <rect x="422" y="240" width="36" height="150" rx="5" fill="url(#barGrad)"  />
    <rect x="468" y="190" width="36" height="200" rx="5" fill="url(#barPink)"  />
    <rect x="514" y="265" width="36" height="125" rx="5" fill="url(#barGrad)"  />
  </svg>
);

/* ── Component ───────────────────────────────────────────────────────────────── */
export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    <Box sx={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden', display: 'flex', alignItems: 'center' }}>
      <WaveBg />

      {/* Logo */}
      <Box sx={{ position: 'absolute', top: 28, left: 36, zIndex: 2 }}>
        <Box component="img" src="/logo.png" alt="Sales Pilot AI CRM" sx={{ height: 56, display: "block" }} />
      </Box>

      {/* Login card */}
      <Box sx={{
        position: 'absolute',
        right: { xs: 16, sm: 48, md: 72 },
        top: '50%',
        transform: 'translateY(-50%)',
        width: { xs: 'calc(100% - 32px)', sm: 370 },
        bgcolor: '#1C2E50',
        borderRadius: '16px',
        p: '36px 36px',
        zIndex: 2,
        boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
      }}>
        <Typography variant="h5" fontWeight={600} color="#fff" textAlign="center" mb="28px" fontSize={22}>
          Войти в Аккаунт
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2, fontSize: 13 }}>{error}</Alert>}

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {[
            { label: 'Email', value: email, onChange: setEmail, type: 'email', autoFocus: true },
            { label: 'Пароль', value: password, onChange: setPassword, type: 'password' },
          ].map(({ label, value, onChange, type, autoFocus }) => (
            <Box key={label}>
              <Typography sx={{ color: 'rgba(255,255,255,0.75)', fontSize: 13, mb: '6px', fontWeight: 500 }}>
                {label}
              </Typography>
              <Box
                component="input"
                type={type}
                required
                autoFocus={autoFocus}
                value={value}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
                sx={{
                  width: '100%',
                  height: 42,
                  bgcolor: '#243558',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: 14,
                  px: '14px',
                  outline: 'none',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s',
                  '&:focus': { borderColor: '#3B7FE8', boxShadow: '0 0 0 2px rgba(59,127,232,0.25)' },
                  '&::placeholder': { color: 'rgba(255,255,255,0.3)' },
                }}
              />
            </Box>
          ))}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{
              mt: '6px',
              height: 46,
              bgcolor: '#3B7FE8',
              fontWeight: 600,
              fontSize: 15,
              borderRadius: '10px',
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': { bgcolor: '#2D6ED6', boxShadow: 'none' },
            }}
          >
            {loading ? <CircularProgress size={22} color="inherit" /> : 'Войти'}
          </Button>
        </Box>

        <Box sx={{ mt: '18px', textAlign: 'center' }}>
          <Typography component="span" sx={{ color: 'rgba(255,255,255,0.5)', fontSize: 13 }}>
            Нет аккаунта?{' '}
          </Typography>
          <Link
            component="button"
            type="button"
            onClick={() => navigate('/register')}
            sx={{ color: '#60B8F8', fontSize: 13, fontWeight: 500, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
          >
            Зарегистрироваться
          </Link>
        </Box>
      </Box>
    </Box>
  );
}
