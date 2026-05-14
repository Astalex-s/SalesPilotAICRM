import { useState } from 'react';
import { Box, Dialog, DialogContent, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/useAuthStore';
import { updateProfile, changePassword } from '../../api/users';

/* ── Avatar color options ────────────────────────────────────────────────────── */
const AVATAR_COLORS = [
  '#0D2144', '#00A8E8', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
];

const ROLE_LABEL: Record<string, { en: string; ru: string }> = {
  admin:    { en: 'Admin',    ru: 'Администратор' },
  manager:  { en: 'Manager',  ru: 'Менеджер' },
  sales_rep: { en: 'Sales Rep', ru: 'Сотрудник' },
};

/* ── Shared input style ──────────────────────────────────────────────────────── */
const inputSx = {
  width: '100%',
  px: '12px', py: '9px',
  border: '1px solid', borderColor: 'divider',
  borderRadius: '8px',
  fontSize: 13,
  fontFamily: 'Inter, sans-serif',
  color: 'text.primary',
  background: '#fff',
  outline: 'none',
  transition: 'border-color 0.15s',
  '&:focus': { borderColor: '#00A8E8' },
  '&:disabled': { bgcolor: 'background.default', color: '#8FA3B8', cursor: 'not-allowed' },
};

/* ── Label ───────────────────────────────────────────────────────────────────── */
function FieldLabel({ text }: { text: string }) {
  return (
    <Typography sx={{
      fontSize: 12, fontWeight: 600, color: '#5E6E82',
      fontFamily: 'Inter, sans-serif', mb: 0.5, textTransform: 'uppercase',
      letterSpacing: '0.05em',
    }}>
      {text}
    </Typography>
  );
}

/* ── Main dialog ─────────────────────────────────────────────────────────────── */
interface UserProfileDialogProps {
  open: boolean;
  onClose: () => void;
}

export default function UserProfileDialog({ open, onClose }: UserProfileDialogProps) {
  const { t, i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);

  const [firstName, setFirstName] = useState(user?.first_name ?? '');
  const [lastName,  setLastName]  = useState(user?.last_name  ?? '');
  const [avatarColor, setAvatarColor] = useState(
    localStorage.getItem('crm-avatar-color') ?? AVATAR_COLORS[0]
  );
  const [currentPw,   setCurrentPw]   = useState('');
  const [newPw,       setNewPw]       = useState('');
  const [confirmPw,   setConfirmPw]   = useState('');
  const [pwError,     setPwError]     = useState('');
  const [saved,       setSaved]       = useState(false);
  const [saving,      setSaving]      = useState(false);
  const [saveError,   setSaveError]   = useState('');
  const [pwSaved,     setPwSaved]     = useState(false);
  const [pwSaving,    setPwSaving]    = useState(false);

  if (!user) return null;

  const lang = i18n.language;
  const roleLabel = ROLE_LABEL[user.role]?.[lang as 'en' | 'ru'] ?? user.role;
  const initials = `${firstName[0] ?? ''}${lastName[0] ?? ''}`.toUpperCase() || '??';

  const handleSaveProfile = async () => {
    if (!firstName.trim() || !lastName.trim()) return;
    setSaving(true);
    setSaveError('');
    try {
      const updated = await updateProfile(firstName.trim(), lastName.trim());
      setUser({ ...user, first_name: updated.first_name, last_name: updated.last_name });
      localStorage.setItem('crm-avatar-color', avatarColor);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      setSaveError(t('profile.errors.saveFailed'));
    } finally {
      setSaving(false);
    }
  };

  const handleSavePassword = async () => {
    setPwError('');
    if (!currentPw) { setPwError(t('profile.errors.currentRequired')); return; }
    if (newPw.length < 8) { setPwError(t('profile.errors.passwordTooShort')); return; }
    if (newPw !== confirmPw) { setPwError(t('profile.errors.passwordMismatch')); return; }
    setPwSaving(true);
    try {
      await changePassword(currentPw, newPw);
      setCurrentPw(''); setNewPw(''); setConfirmPw('');
      setPwSaved(true);
      setTimeout(() => setPwSaved(false), 2500);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setPwError(msg ?? t('profile.errors.saveFailed'));
    } finally {
      setPwSaving(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        elevation: 0,
        sx: {
          borderRadius: '16px',
          border: '1px solid', borderColor: 'divider',
          boxShadow: '0 16px 48px rgba(13,33,68,0.14)',
          overflow: 'hidden',
        },
      }}
    >
      {/* Header */}
      <Box sx={{
        px: 3, pt: 3, pb: 2,
        borderBottom: '1px solid #F3F6FA',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <Typography sx={{
          fontSize: 18, fontWeight: 700, color: 'text.primary',
          fontFamily: 'Inter, sans-serif',
        }}>
          {t('profile.title')}
        </Typography>
        <Box
          onClick={onClose}
          sx={{
            color: '#8FA3B8', cursor: 'pointer', display: 'flex',
            p: '6px', borderRadius: '8px',
            '&:hover': { color: '#3E4850', bgcolor: 'action.hover' },
          }}
        >
          <svg width={18} height={18} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </Box>
      </Box>

      <DialogContent sx={{ p: 3 }}>

        {/* Avatar + basic info */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2.5, mb: 3 }}>
          <Box sx={{ position: 'relative' }}>
            <Box sx={{
              width: 72, height: 72, borderRadius: '50%',
              bgcolor: avatarColor, color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 24, fontWeight: 700, fontFamily: 'Inter, sans-serif',
              border: '3px solid #E8EFF7',
              flexShrink: 0,
            }}>
              {initials}
            </Box>
          </Box>
          <Box>
            <Typography sx={{
              fontSize: 18, fontWeight: 700, color: 'text.primary',
              fontFamily: 'Inter, sans-serif', lineHeight: 1.2,
            }}>
              {user.first_name} {user.last_name}
            </Typography>
            <Typography sx={{
              fontSize: 13, color: '#8FA3B8', fontFamily: 'Inter, sans-serif', mt: '2px',
            }}>
              {user.email}
            </Typography>
            <Box sx={{
              display: 'inline-flex', mt: '6px',
              px: '8px', py: '3px', borderRadius: '999px',
              bgcolor: 'rgba(0,168,232,0.1)', border: '1px solid rgba(0,168,232,0.2)',
            }}>
              <Typography sx={{
                fontSize: 11, fontWeight: 600, color: '#00A8E8',
                fontFamily: 'Inter, sans-serif', textTransform: 'capitalize',
              }}>
                {roleLabel}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Avatar color picker */}
        <Box sx={{ mb: 3 }}>
          <FieldLabel text={t('profile.avatarColor')} />
          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
            {AVATAR_COLORS.map((c) => (
              <Box
                key={c}
                onClick={() => setAvatarColor(c)}
                sx={{
                  width: 28, height: 28, borderRadius: '50%', bgcolor: c,
                  cursor: 'pointer', border: avatarColor === c ? '3px solid #00A8E8' : '2px solid #E8EFF7',
                  transition: 'border 0.15s, transform 0.15s',
                  '&:hover': { transform: 'scale(1.15)' },
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Edit name fields */}
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
          <Box>
            <FieldLabel text={t('profile.firstName')} />
            <Box
              component="input"
              type="text"
              value={firstName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFirstName(e.target.value)}
              sx={inputSx}
            />
          </Box>
          <Box>
            <FieldLabel text={t('profile.lastName')} />
            <Box
              component="input"
              type="text"
              value={lastName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLastName(e.target.value)}
              sx={inputSx}
            />
          </Box>
        </Box>

        {/* Email (read-only) */}
        <Box sx={{ mb: 3 }}>
          <FieldLabel text={t('profile.email')} />
          <Box
            component="input"
            type="email"
            value={user.email}
            disabled
            sx={inputSx}
          />
        </Box>

        {/* Save profile button */}
        {saveError && (
          <Typography sx={{ fontSize: 12, color: '#EF4444', fontFamily: 'Inter, sans-serif', mb: 1 }}>
            {saveError}
          </Typography>
        )}
        <Box
          component="button"
          onClick={handleSaveProfile}
          disabled={saving}
          sx={{
            width: '100%',
            py: '10px',
            borderRadius: '8px',
            border: 'none',
            bgcolor: saved ? '#10B981' : '#00A8E8',
            color: '#fff',
            fontSize: 14, fontWeight: 600, fontFamily: 'Inter, sans-serif',
            cursor: saving ? 'default' : 'pointer',
            opacity: saving ? 0.7 : 1,
            transition: 'background 0.2s',
            '&:hover': { bgcolor: saved ? '#10B981' : saving ? '#00A8E8' : '#0096D1' },
            mb: 3,
          }}
        >
          {saved ? t('profile.saved') : saving ? t('profile.saving') : t('profile.saveChanges')}
        </Box>

        {/* Divider */}
        <Box sx={{ height: 1, bgcolor: '#F3F6FA', mb: 3 }} />

        {/* Change password section */}
        <Typography sx={{
          fontSize: 14, fontWeight: 600, color: 'text.primary',
          fontFamily: 'Inter, sans-serif', mb: 0.5,
        }}>
          {t('profile.changePassword')}
        </Typography>
        <Typography sx={{
          fontSize: 12, color: '#8FA3B8',
          fontFamily: 'Inter, sans-serif', mb: 2,
        }}>
          {t('profile.passwordHint')}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <Box>
            <FieldLabel text={t('profile.currentPassword')} />
            <Box
              component="input"
              type="password"
              value={currentPw}
              placeholder="••••••••"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentPw(e.target.value)}
              sx={inputSx}
            />
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
            <Box>
              <FieldLabel text={t('profile.newPassword')} />
              <Box
                component="input"
                type="password"
                value={newPw}
                placeholder="••••••••"
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPw(e.target.value)}
                sx={inputSx}
              />
            </Box>
            <Box>
              <FieldLabel text={t('profile.confirmPassword')} />
              <Box
                component="input"
                type="password"
                value={confirmPw}
                placeholder="••••••••"
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirmPw(e.target.value)}
                sx={inputSx}
              />
            </Box>
          </Box>
        </Box>

        {pwError && (
          <Typography sx={{
            fontSize: 12, color: '#EF4444', fontFamily: 'Inter, sans-serif', mt: 1,
          }}>
            {pwError}
          </Typography>
        )}

        <Box
          component="button"
          onClick={handleSavePassword}
          disabled={pwSaving}
          sx={{
            width: '100%',
            py: '10px',
            mt: 2,
            borderRadius: '8px',
            border: '1px solid', borderColor: 'divider',
            bgcolor: pwSaved ? '#10B981' : '#fff',
            color: pwSaved ? '#fff' : '#0D2144',
            fontSize: 14, fontWeight: 600, fontFamily: 'Inter, sans-serif',
            cursor: pwSaving ? 'default' : 'pointer',
            opacity: pwSaving ? 0.7 : 1,
            transition: 'all 0.2s',
            '&:hover': { bgcolor: pwSaved ? '#10B981' : pwSaving ? '#fff' : '#F5F8FC', borderColor: '#BDC8D1' },
          }}
        >
          {pwSaved ? t('profile.passwordChanged') : pwSaving ? t('profile.saving') : t('profile.changePassword')}
        </Box>

      </DialogContent>
    </Dialog>
  );
}
