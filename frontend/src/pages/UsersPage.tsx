import BadgeIcon from '@mui/icons-material/Badge';
import LockIcon from '@mui/icons-material/Lock';
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';
import SearchIcon from '@mui/icons-material/Search';
import ShieldIcon from '@mui/icons-material/Shield';
import {
  Alert,
  Box,
  CircularProgress,
  Grid,
  InputAdornment,
  MenuItem,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import EmptyState from '../components/common/EmptyState';
import { listUsers, updateUserRole } from '../api/users';
import { useAuthStore } from '../store/useAuthStore';
import type { User, UserRole } from '../types/auth';

/* ── Design tokens ── */
const CARD = {
  background: '#FFFFFF',
  border: '1px solid #E2EAF4',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(13,33,68,0.07)',
};

/* ── Role config ── */
const ROLE_STYLE: Record<UserRole, { bg: string; color: string; icon: React.ReactNode }> = {
  admin:     { bg: '#0D2144',  color: '#FFFFFF', icon: <ShieldIcon sx={{ fontSize: 16 }} /> },
  manager:   { bg: '#00A8E8',  color: '#FFFFFF', icon: <ManageAccountsIcon sx={{ fontSize: 16 }} /> },
  sales_rep: { bg: '#E8F4FF',  color: '#0D2144', icon: <BadgeIcon sx={{ fontSize: 16 }} /> },
};

/* ── Avatar ── */
const AVATAR_PALETTE = ['#00A8E8', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#0D2144'];

function avatarColor(name: string) {
  return AVATAR_PALETTE[name.charCodeAt(0) % AVATAR_PALETTE.length];
}

/* ── Role badge ── */
function RoleBadge({ role }: { role: UserRole }) {
  const { t } = useTranslation();
  const s = ROLE_STYLE[role];
  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.5,
        px: 1.25,
        py: 0.4,
        borderRadius: '20px',
        bgcolor: s.bg,
        color: s.color,
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {s.icon}
      {t(`users.roles.${role}`)}
    </Box>
  );
}

/* ── Role explanation cards ── */
const ROLE_CARDS: Array<{ role: UserRole; descKey: string }> = [
  { role: 'admin',     descKey: 'users.roleCards.admin.desc' },
  { role: 'manager',   descKey: 'users.roleCards.manager.desc' },
  { role: 'sales_rep', descKey: 'users.roleCards.sales_rep.desc' },
];

function RoleExplanationCards() {
  const { t } = useTranslation();
  return (
    <Grid container spacing={2} sx={{ mb: 3 }}>
      {ROLE_CARDS.map(({ role, descKey }) => {
        const s = ROLE_STYLE[role];
        const isAdmin = role === 'admin';
        return (
          <Grid item xs={12} sm={4} key={role}>
            <Box
              sx={{
                ...CARD,
                background: isAdmin ? '#0D2144' : '#FFFFFF',
                p: 2.5,
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: '10px',
                  bgcolor: isAdmin ? 'rgba(255,255,255,0.1)' : `${s.bg}1A`,
                  color: isAdmin ? '#FFFFFF' : s.bg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {s.icon}
              </Box>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 700,
                  fontSize: 15,
                  color: isAdmin ? '#FFFFFF' : '#0D2144',
                }}
              >
                {t(`users.roles.${role}`)}
              </Typography>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  color: isAdmin ? 'rgba(255,255,255,0.65)' : '#94A3B8',
                  lineHeight: 1.5,
                }}
              >
                {t(descKey)}
              </Typography>
            </Box>
          </Grid>
        );
      })}
    </Grid>
  );
}

/* ── Skeleton rows ── */
function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 4 }).map((_, i) => (
        <TableRow key={i} sx={{ height: 60 }}>
          <TableCell>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Skeleton variant="circular" width={36} height={36} />
              <Box>
                <Skeleton variant="text" width={120} height={18} />
                <Skeleton variant="text" width={160} height={14} />
              </Box>
            </Box>
          </TableCell>
          <TableCell><Skeleton variant="rounded" width={80} height={24} sx={{ borderRadius: '20px' }} /></TableCell>
          <TableCell><Skeleton variant="rounded" width={64} height={22} sx={{ borderRadius: '20px' }} /></TableCell>
          <TableCell><Skeleton variant="rounded" width={120} height={32} sx={{ borderRadius: '10px' }} /></TableCell>
        </TableRow>
      ))}
    </>
  );
}

/* ── Main page ── */
export default function UsersPage() {
  const { t } = useTranslation();
  const currentUser = useAuthStore((s) => s.user);

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    listUsers()
      .then(setUsers)
      .catch((err) => setError(err instanceof Error ? err.message : t('users.loadError')))
      .finally(() => setLoading(false));
  }, []);

  const handleRoleChange = async (userId: string, role: UserRole) => {
    setUpdating(userId);
    try {
      const updated = await updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err) {
      setError(err instanceof Error ? err.message : t('users.updateError'));
    } finally {
      setUpdating(null);
    }
  };

  const filtered = useMemo(() => {
    if (!search.trim()) return users;
    const q = search.toLowerCase();
    return users.filter(
      (u) =>
        u.first_name.toLowerCase().includes(q) ||
        u.last_name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q),
    );
  }, [users, search]);

  return (
    <Box>
      {/* ── Header ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Typography
          sx={{ fontFamily: 'Inter, sans-serif', fontSize: 24, fontWeight: 700, color: '#0D2144' }}
        >
          {t('users.title')}
        </Typography>
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 0.5,
            px: 1.25,
            py: 0.4,
            borderRadius: '20px',
            bgcolor: 'rgba(239,68,68,0.1)',
            color: '#DC2626',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          <LockIcon sx={{ fontSize: 12 }} />
          {t('users.adminOnly')}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      {/* ── Role explanation cards ── */}
      <RoleExplanationCards />

      {/* ── Search ── */}
      <Box sx={{ mb: 2 }}>
        <TextField
          size="small"
          placeholder={t('users.search')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#94A3B8', fontSize: 18 }} />
              </InputAdornment>
            ),
          }}
          sx={{
            width: 280,
            '& .MuiOutlinedInput-root': {
              borderRadius: '10px',
              bgcolor: '#FFFFFF',
              fontFamily: 'Inter, sans-serif',
              fontSize: 14,
              '& fieldset': { borderColor: '#E2EAF4' },
              '&:hover fieldset': { borderColor: '#CBD5E8' },
              '&.Mui-focused fieldset': { borderColor: '#00A8E8', borderWidth: 2 },
            },
          }}
        />
      </Box>

      {/* ── Table ── */}
      <Box sx={CARD}>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {[
                t('users.table.member'),
                t('users.table.role'),
                t('users.table.status'),
                t('users.table.actions'),
              ].map((label, i) => (
                <TableCell
                  key={i}
                  sx={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    fontWeight: 500,
                    letterSpacing: '0.07em',
                    textTransform: 'uppercase',
                    color: '#94A3B8',
                    border: 'none',
                    py: 1.5,
                    width: i === 0 ? '40%' : i === 3 ? '20%' : '20%',
                  }}
                >
                  {label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              <SkeletonRows />
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} sx={{ border: 'none' }}>
                  <EmptyState
                    icon="users"
                    title={t('users.noUsers')}
                    subtitle={t('users.noUsersSubtitle')}
                  />
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((user) => {
                const color = avatarColor(user.first_name);
                const isCurrentUser = user.id === currentUser?.id;

                return (
                  <TableRow
                    key={user.id}
                    sx={{
                      height: 60,
                      bgcolor: isCurrentUser ? 'rgba(0,168,232,0.03)' : 'transparent',
                      borderLeft: isCurrentUser ? '3px solid #00A8E8' : '3px solid transparent',
                      '& td': { border: 'none', borderTop: '1px solid #F0F5FF' },
                    }}
                  >
                    {/* Avatar + name */}
                    <TableCell sx={{ py: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Box
                          sx={{
                            width: 36,
                            height: 36,
                            borderRadius: '50%',
                            bgcolor: color,
                            color: '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontFamily: 'Inter, sans-serif',
                            fontSize: 13,
                            fontWeight: 700,
                            flexShrink: 0,
                          }}
                        >
                          {`${user.first_name[0]}${user.last_name[0]}`.toUpperCase()}
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                            <Typography
                              sx={{
                                fontFamily: 'Inter, sans-serif',
                                fontWeight: 600,
                                fontSize: 14,
                                color: '#0D2144',
                              }}
                            >
                              {user.first_name} {user.last_name}
                            </Typography>
                            {isCurrentUser && (
                              <Box
                                sx={{
                                  px: 0.75,
                                  py: 0.1,
                                  borderRadius: '20px',
                                  bgcolor: 'rgba(0,168,232,0.12)',
                                  color: '#0090CC',
                                  fontFamily: 'Inter',
                                  fontSize: 11,
                                  fontWeight: 600,
                                }}
                              >
                                {t('users.you')}
                              </Box>
                            )}
                          </Box>
                          <Typography
                            sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}
                          >
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>

                    {/* Role */}
                    <TableCell sx={{ py: 1 }}>
                      <RoleBadge role={user.role} />
                    </TableCell>

                    {/* Status */}
                    <TableCell sx={{ py: 1 }}>
                      <Box
                        sx={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          px: 1.25,
                          py: 0.4,
                          borderRadius: '20px',
                          bgcolor: user.is_active
                            ? 'rgba(16,185,129,0.12)'
                            : 'rgba(239,68,68,0.12)',
                          color: user.is_active ? '#059669' : '#DC2626',
                          fontFamily: 'Inter, sans-serif',
                          fontSize: 12,
                          fontWeight: 600,
                        }}
                      >
                        {t(user.is_active ? 'users.status.active' : 'users.status.inactive')}
                      </Box>
                    </TableCell>

                    {/* Actions — role select */}
                    <TableCell sx={{ py: 1 }}>
                      {updating === user.id ? (
                        <CircularProgress size={20} sx={{ color: '#00A8E8' }} />
                      ) : (
                        <Tooltip title={isCurrentUser ? t('users.cantEditSelf') : ''}>
                          <span>
                            <Select<UserRole>
                              value={user.role}
                              disabled={isCurrentUser}
                              onChange={(e) => handleRoleChange(user.id, e.target.value as UserRole)}
                              size="small"
                              sx={{
                                borderRadius: '10px',
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 13,
                                minWidth: 130,
                                '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E2EAF4' },
                                '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#CBD5E8' },
                                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#00A8E8',
                                  borderWidth: 2,
                                },
                                '&.Mui-disabled': { opacity: 0.5 },
                              }}
                            >
                              {(['admin', 'manager', 'sales_rep'] as UserRole[]).map((r) => (
                                <MenuItem
                                  key={r}
                                  value={r}
                                  sx={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}
                                >
                                  {t(`users.roles.${r}`)}
                                </MenuItem>
                              ))}
                            </Select>
                          </span>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Box>
    </Box>
  );
}
