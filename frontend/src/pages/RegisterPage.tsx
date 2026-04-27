import PersonAddIcon from '@mui/icons-material/PersonAdd';
import {
  Alert,
  Avatar,
  Box,
  Button,
  CircularProgress,
  Container,
  Link,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register, login, getMe } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';

export default function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (form.password !== form.confirm_password) {
      setError('Пароли не совпадают');
      return;
    }
    setLoading(true);
    try {
      await register({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        password: form.password,
      });
      // Auto-login after registration
      const tokenData = await login({ email: form.email, password: form.password });
      localStorage.setItem('crm-auth', JSON.stringify({ state: { token: tokenData.access_token } }));
      const user = await getMe();
      setAuth(tokenData.access_token, user);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box
        sx={{
          mt: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Avatar sx={{ bgcolor: 'secondary.main' }}>
          <PersonAddIcon />
        </Avatar>
        <Typography variant="h5" fontWeight={700}>
          Регистрация
        </Typography>

        {error && <Alert severity="error" sx={{ width: '100%' }}>{error}</Alert>}

        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField label="Имя" fullWidth margin="dense" required value={form.first_name} onChange={set('first_name')} autoFocus />
          <TextField label="Фамилия" fullWidth margin="dense" required value={form.last_name} onChange={set('last_name')} />
          <TextField label="E-mail" type="email" fullWidth margin="dense" required value={form.email} onChange={set('email')} />
          <TextField label="Пароль" type="password" fullWidth margin="dense" required inputProps={{ minLength: 6 }} value={form.password} onChange={set('password')} />
          <TextField label="Повторите пароль" type="password" fullWidth margin="dense" required value={form.confirm_password} onChange={set('confirm_password')} />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            sx={{ mt: 2, mb: 1 }}
          >
            {loading ? <CircularProgress size={22} color="inherit" /> : 'Зарегистрироваться'}
          </Button>
          <Box sx={{ textAlign: 'center' }}>
            <Link
              component="button"
              type="button"
              variant="body2"
              onClick={() => navigate('/login')}
            >
              Уже есть аккаунт? Войти
            </Link>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}
