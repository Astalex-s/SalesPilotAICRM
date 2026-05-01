import { useState } from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSettingsStore } from '../store/useSettingsStore';
import { useUIStore } from '../store/useUIStore';

/* ── Design tokens ───────────────────────────────────────────────────────────── */
const C = {
  navy:    '#0D2144',
  cyan:    '#00A8E8',
  bg:      '#F7F9FC',
  card:    '#FFFFFF',
  border:  '#E8EFF7',
  text:    '#191C1E',
  sub:     '#5E6E82',
  muted:   '#8FA3B8',
};

/* ── Section card wrapper ────────────────────────────────────────────────────── */
function SettingsSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Box sx={{
      bgcolor: C.card, border: `1px solid ${C.border}`,
      borderRadius: '12px', overflow: 'hidden',
    }}>
      <Box sx={{
        px: 3, py: 2,
        borderBottom: `1px solid ${C.border}`,
        bgcolor: '#FAFCFE',
      }}>
        <Typography sx={{
          fontSize: 13, fontWeight: 600, color: C.navy,
          fontFamily: 'Inter, sans-serif', textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          {title}
        </Typography>
      </Box>
      <Box>{children}</Box>
    </Box>
  );
}

/* ── Setting row with toggle ─────────────────────────────────────────────────── */
function ToggleRow({
  label, desc, checked, onChange, disabled,
}: {
  label: string; desc?: string; checked: boolean; onChange: (v: boolean) => void; disabled?: boolean;
}) {
  return (
    <Box sx={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      px: 3, py: 2,
      borderBottom: `1px solid ${C.border}`,
      '&:last-child': { borderBottom: 'none' },
      opacity: disabled ? 0.5 : 1,
    }}>
      <Box>
        <Typography sx={{ fontSize: 14, fontWeight: 500, color: C.text, fontFamily: 'Inter, sans-serif' }}>
          {label}
        </Typography>
        {desc && (
          <Typography sx={{ fontSize: 12, color: C.muted, fontFamily: 'Inter, sans-serif', mt: '2px' }}>
            {desc}
          </Typography>
        )}
      </Box>
      <Box
        onClick={() => !disabled && onChange(!checked)}
        sx={{
          width: 44, height: 24, borderRadius: '999px',
          bgcolor: checked ? C.cyan : '#D1DCE8',
          position: 'relative', cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s', flexShrink: 0,
        }}
      >
        <Box sx={{
          position: 'absolute',
          top: 3, left: checked ? 23 : 3,
          width: 18, height: 18, borderRadius: '50%',
          bgcolor: '#fff',
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
          transition: 'left 0.2s',
        }} />
      </Box>
    </Box>
  );
}

/* ── Setting row with text value / badge ─────────────────────────────────────── */
function InfoRow({ label, value, badge }: { label: string; value: string; badge?: string }) {
  return (
    <Box sx={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      px: 3, py: 2,
      borderBottom: `1px solid ${C.border}`,
      '&:last-child': { borderBottom: 'none' },
    }}>
      <Typography sx={{ fontSize: 14, fontWeight: 500, color: C.text, fontFamily: 'Inter, sans-serif' }}>
        {label}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {badge && (
          <Box sx={{
            px: '8px', py: '3px', borderRadius: '999px',
            bgcolor: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)',
          }}>
            <Typography sx={{ fontSize: 11, fontWeight: 600, color: '#10B981', fontFamily: 'Inter, sans-serif' }}>
              {badge}
            </Typography>
          </Box>
        )}
        <Typography sx={{ fontSize: 13, color: C.sub, fontFamily: 'Inter, sans-serif' }}>
          {value}
        </Typography>
      </Box>
    </Box>
  );
}

/* ── Language selector row ───────────────────────────────────────────────────── */
function LangRow({ label }: { label: string }) {
  const { i18n, t } = useTranslation();
  const current = i18n.language;

  const toggle = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('crm-lang', lang);
  };

  return (
    <Box sx={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      px: 3, py: 2,
      borderBottom: `1px solid ${C.border}`,
      '&:last-child': { borderBottom: 'none' },
    }}>
      <Typography sx={{ fontSize: 14, fontWeight: 500, color: C.text, fontFamily: 'Inter, sans-serif' }}>
        {label}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1 }}>
        {(['en', 'ru'] as const).map((lang) => (
          <Box
            key={lang}
            onClick={() => toggle(lang)}
            sx={{
              px: '14px', py: '6px', borderRadius: '8px',
              border: `1px solid ${current === lang ? C.cyan : C.border}`,
              bgcolor: current === lang ? 'rgba(0,168,232,0.08)' : '#fff',
              color: current === lang ? C.cyan : C.sub,
              fontSize: 13, fontWeight: 600, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer', transition: 'all 0.15s',
              '&:hover': { borderColor: C.cyan, color: C.cyan },
            }}
          >
            {t(`settings.language.${lang}`)}
          </Box>
        ))}
      </Box>
    </Box>
  );
}

/* ── Main Page ───────────────────────────────────────────────────────────────── */
export default function SettingsPage() {
  const { t } = useTranslation();
  const settings = useSettingsStore();
  const { sidebarOpen, setSidebarOpen } = useUIStore();
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <Box sx={{ bgcolor: C.bg, minHeight: '100vh', p: 3 }}>

      {/* Page header */}
      <Box sx={{ mb: 3 }}>
        <Typography sx={{
          fontSize: 22, fontWeight: 700, color: C.navy,
          fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em',
        }}>
          {t('settings.title')}
        </Typography>
        <Typography sx={{
          fontSize: 14, color: C.muted, fontFamily: 'Inter, sans-serif', mt: '4px',
        }}>
          {t('settings.subtitle')}
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, maxWidth: 680 }}>

        {/* Appearance */}
        <SettingsSection title={t('settings.sections.appearance')}>
          <ToggleRow
            label={t('settings.appearance.sidebarDefault')}
            desc={t('settings.appearance.sidebarDefaultDesc')}
            checked={sidebarOpen}
            onChange={(v) => {
              setSidebarOpen(v);
              settings.update({ sidebarDefaultOpen: v });
            }}
          />
          <ToggleRow
            label={t('settings.appearance.themeDark')}
            checked={false}
            onChange={() => {}}
            disabled
          />
        </SettingsSection>

        {/* Language */}
        <SettingsSection title={t('settings.sections.language')}>
          <LangRow label={t('settings.language.appLanguage')} />
        </SettingsSection>

        {/* Notifications */}
        <SettingsSection title={t('settings.sections.notifications')}>
          <ToggleRow
            label={t('settings.notifications.emailNotifs')}
            desc={t('settings.notifications.emailNotifsDesc')}
            checked={settings.notifEmail}
            onChange={(v) => settings.update({ notifEmail: v })}
          />
          <ToggleRow
            label={t('settings.notifications.dealNotifs')}
            desc={t('settings.notifications.dealNotifsDesc')}
            checked={settings.notifDeal}
            onChange={(v) => settings.update({ notifDeal: v })}
          />
          <ToggleRow
            label={t('settings.notifications.leadNotifs')}
            desc={t('settings.notifications.leadNotifsDesc')}
            checked={settings.notifLead}
            onChange={(v) => settings.update({ notifLead: v })}
          />
          <ToggleRow
            label={t('settings.notifications.systemNotifs')}
            desc={t('settings.notifications.systemNotifsDesc')}
            checked={settings.notifSystem}
            onChange={(v) => settings.update({ notifSystem: v })}
          />
        </SettingsSection>

        {/* Privacy */}
        <SettingsSection title={t('settings.sections.privacy')}>
          <InfoRow
            label={t('settings.privacy.twoFactor')}
            value={t('settings.privacy.twoFactorDesc')}
          />
          <InfoRow
            label={t('settings.privacy.activeSessions')}
            value={t('settings.privacy.activeSessionsDesc')}
            badge="1"
          />
        </SettingsSection>

        {/* Save button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Box
            component="button"
            onClick={handleSave}
            sx={{
              px: 3, py: '10px',
              borderRadius: '8px',
              border: 'none',
              bgcolor: saved ? '#10B981' : C.cyan,
              color: '#fff',
              fontSize: 14, fontWeight: 600, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer',
              transition: 'background 0.2s',
              '&:hover': { bgcolor: saved ? '#10B981' : '#0096D1' },
            }}
          >
            {saved ? t('settings.saved') : t('settings.saveChanges')}
          </Box>
        </Box>

      </Box>
    </Box>
  );
}
