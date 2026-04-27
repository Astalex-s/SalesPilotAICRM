import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  FormControl,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { listUsers, updateUserRole } from '../api/users';
import type { User, UserRole } from '../types/auth';

const ROLE_LABEL: Record<UserRole, string> = {
  admin: 'Администратор',
  manager: 'Менеджер',
  sales_rep: 'Сотрудник',
};

const ROLE_COLOR: Record<UserRole, 'error' | 'warning' | 'default'> = {
  admin: 'error',
  manager: 'warning',
  sales_rep: 'default',
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    listUsers()
      .then(setUsers)
      .catch((err) => setError(err instanceof Error ? err.message : 'Ошибка загрузки'))
      .finally(() => setLoading(false));
  }, []);

  const handleRoleChange = async (userId: string, role: UserRole) => {
    setUpdating(userId);
    try {
      const updated = await updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления роли');
    } finally {
      setUpdating(null);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <AdminPanelSettingsIcon color="primary" />
        <Typography variant="h5" fontWeight={700}>
          Управление пользователями
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Имя</TableCell>
                <TableCell>E-mail</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Роль</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                    Пользователи не найдены.
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>{user.first_name} {user.last_name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Активен' : 'Заблокирован'}
                        color={user.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {updating === user.id ? (
                        <CircularProgress size={20} />
                      ) : (
                        <FormControl size="small">
                          <Select<UserRole>
                            value={user.role}
                            onChange={(e) => handleRoleChange(user.id, e.target.value as UserRole)}
                            renderValue={(v) => (
                              <Chip
                                label={ROLE_LABEL[v]}
                                color={ROLE_COLOR[v]}
                                size="small"
                              />
                            )}
                          >
                            <MenuItem value="admin">Администратор</MenuItem>
                            <MenuItem value="manager">Менеджер</MenuItem>
                            <MenuItem value="sales_rep">Сотрудник</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
