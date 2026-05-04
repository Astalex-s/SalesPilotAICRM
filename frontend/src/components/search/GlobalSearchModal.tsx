/**
 * GlobalSearchModal — поиск по всему приложению.
 *
 * Открывается по клику на TopBar search pill или по Ctrl+K / ⌘K.
 * Ищет лидов и сделки через существующие API, фильтрует на клиенте.
 * Группировка результатов: Leads | Deals. Клик → навигация.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { leadsApi } from '../../api/leads';
import { dealsApi } from '../../api/deals';
import type { Lead } from '../../types/lead';
import type { Deal } from '../../types/deal';

/* ── Shared styles ───────────────────────────────────────────────────────────── */
const C = {
  navy:   '#0D2144',
  cyan:   '#00A8E8',
  bg:     '#F7F9FC',
  border: '#E8EFF7',
  text:   '#191C1E',
  sub:    '#5E6E82',
  muted:  '#8FA3B8',
  hover:  '#F5F8FC',
};

/* ── Result row ──────────────────────────────────────────────────────────────── */
function ResultRow({
  label, sub, badge, badgeColor, onClick, active,
}: {
  label: string; sub?: string; badge?: string; badgeColor?: string;
  onClick: () => void; active: boolean;
}) {
  return (
    <Box
      onClick={onClick}
      sx={{
        display: 'flex', alignItems: 'center', gap: 1.5,
        px: 2, py: 1.25, cursor: 'pointer', borderRadius: '8px', mx: 1,
        bgcolor: active ? 'rgba(0,168,232,0.08)' : 'transparent',
        '&:hover': { bgcolor: 'rgba(0,168,232,0.06)' },
        transition: 'background 0.1s',
      }}
    >
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography sx={{
          fontSize: 13, fontWeight: 500, color: C.text,
          fontFamily: 'Inter, sans-serif',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {label}
        </Typography>
        {sub && (
          <Typography sx={{
            fontSize: 11, color: C.muted, fontFamily: 'Inter, sans-serif',
            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
          }}>
            {sub}
          </Typography>
        )}
      </Box>
      {badge && (
        <Box sx={{
          px: '7px', py: '2px', borderRadius: '999px', flexShrink: 0,
          bgcolor: badgeColor ? `${badgeColor}18` : 'rgba(0,168,232,0.1)',
          border: `1px solid ${badgeColor ? `${badgeColor}40` : 'rgba(0,168,232,0.25)'}`,
          fontSize: 10, fontWeight: 600, color: badgeColor ?? C.cyan,
          fontFamily: 'Inter, sans-serif', textTransform: 'capitalize', letterSpacing: '0.02em',
        }}>
          {badge}
        </Box>
      )}
    </Box>
  );
}

/* ── Section header ──────────────────────────────────────────────────────────── */
function SectionLabel({ label, count }: { label: string; count: number }) {
  return (
    <Box sx={{ px: 3, pt: 1.5, pb: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography sx={{
        fontSize: 10, fontWeight: 700, color: C.muted, fontFamily: 'Inter, sans-serif',
        textTransform: 'uppercase', letterSpacing: '0.08em',
      }}>
        {label}
      </Typography>
      <Box sx={{
        px: '5px', py: '1px', borderRadius: '999px',
        bgcolor: C.bg, border: `1px solid ${C.border}`,
        fontSize: 10, fontWeight: 600, color: C.muted, fontFamily: 'Inter, sans-serif',
      }}>
        {count}
      </Box>
    </Box>
  );
}

/* ── Status badge colors ─────────────────────────────────────────────────────── */
const LEAD_STATUS_COLOR: Record<string, string> = {
  new: '#00A8E8', contacted: '#F59E0B', qualified: '#10B981',
  unqualified: '#EF4444', converted: '#8B5CF6',
};
const DEAL_STATUS_COLOR: Record<string, string> = {
  open: '#10B981', won: '#00A8E8', lost: '#EF4444',
};

/* ── Main modal ──────────────────────────────────────────────────────────────── */
export interface GlobalSearchModalProps {
  open: boolean;
  onClose: () => void;
}

export default function GlobalSearchModal({ open, onClose }: GlobalSearchModalProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [query, setQuery] = useState('');
  const [leads, setLeads] = useState<Lead[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load all data when modal opens
  useEffect(() => {
    if (!open) return;
    setQuery('');
    setActiveIdx(0);
    inputRef.current?.focus();

    setLoading(true);
    Promise.all([leadsApi.list(), dealsApi.list()])
      .then(([l, d]) => { setLeads(l); setDeals(d); })
      .finally(() => setLoading(false));
  }, [open]);

  // Filter results client-side
  const q = query.trim().toLowerCase();
  const filteredLeads = useMemo(() => {
    if (!q) return [];
    return leads.filter((l) =>
      `${l.first_name} ${l.last_name}`.toLowerCase().includes(q) ||
      l.email.toLowerCase().includes(q) ||
      (l.company ?? '').toLowerCase().includes(q)
    ).slice(0, 6);
  }, [leads, q]);

  const filteredDeals = useMemo(() => {
    if (!q) return [];
    return deals.filter((d) =>
      d.title.toLowerCase().includes(q) ||
      (d.company ?? '').toLowerCase().includes(q) ||
      (d.contact_name ?? '').toLowerCase().includes(q)
    ).slice(0, 6);
  }, [deals, q]);

  // Flat list for keyboard navigation
  type ResultItem = { key: string; onClick: () => void };
  const allResults: ResultItem[] = useMemo(() => [
    ...filteredLeads.map((l) => ({ key: `lead-${l.id}`, onClick: () => { navigate(`/leads/${l.id}`); onClose(); } })),
    ...filteredDeals.map((d) => ({ key: `deal-${d.id}`, onClick: () => { navigate('/deals'); onClose(); } })),
  ], [filteredLeads, filteredDeals, navigate, onClose]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') { onClose(); return; }
    if (e.key === 'ArrowDown') { e.preventDefault(); setActiveIdx((i) => Math.min(i + 1, allResults.length - 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActiveIdx((i) => Math.max(i - 1, 0)); }
    if (e.key === 'Enter' && allResults[activeIdx]) { allResults[activeIdx].onClick(); }
  };

  if (!open) return null;

  const hasResults = filteredLeads.length > 0 || filteredDeals.length > 0;
  const showEmpty = q.length > 0 && !loading && !hasResults;
  const showHint = !q;

  return (
    <>
      {/* Backdrop */}
      <Box
        onClick={onClose}
        sx={{
          position: 'fixed', inset: 0, zIndex: 1200,
          bgcolor: 'rgba(13,33,68,0.35)',
          backdropFilter: 'blur(4px)',
          animation: 'fadeIn 0.15s ease',
          '@keyframes fadeIn': { from: { opacity: 0 }, to: { opacity: 1 } },
        }}
      />

      {/* Modal */}
      <Box
        sx={{
          position: 'fixed', top: '15%', left: '50%', transform: 'translateX(-50%)',
          zIndex: 1201, width: '100%', maxWidth: 560,
          bgcolor: '#fff', borderRadius: '16px',
          border: `1px solid ${C.border}`,
          boxShadow: '0 24px 64px rgba(13,33,68,0.18)',
          overflow: 'hidden',
          animation: 'slideDown 0.18s ease',
          '@keyframes slideDown': { from: { opacity: 0, transform: 'translateX(-50%) translateY(-8px)' }, to: { opacity: 1, transform: 'translateX(-50%) translateY(0)' } },
        }}
      >
        {/* Search input */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 2, py: 1.5, borderBottom: `1px solid ${C.border}` }}>
          <Box sx={{ color: C.muted, display: 'flex', flexShrink: 0 }}>
            {loading ? (
              <CircularProgress size={18} sx={{ color: C.cyan }} />
            ) : (
              <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            )}
          </Box>
          <Box
            component="input"
            ref={inputRef}
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => { setQuery(e.target.value); setActiveIdx(0); }}
            onKeyDown={handleKeyDown}
            placeholder={t('search.placeholder')}
            sx={{
              flex: 1, border: 'none', outline: 'none', background: 'transparent',
              fontSize: 15, fontFamily: 'Inter, sans-serif', color: C.text,
              '&::placeholder': { color: C.muted },
            }}
          />
          <Box
            onClick={onClose}
            sx={{
              px: '6px', py: '2px', borderRadius: '5px',
              border: `1px solid ${C.border}`,
              fontSize: 11, fontFamily: 'Inter, sans-serif', color: C.muted,
              cursor: 'pointer', flexShrink: 0,
              '&:hover': { color: C.text },
            }}
          >
            Esc
          </Box>
        </Box>

        {/* Results */}
        <Box sx={{ maxHeight: 400, overflowY: 'auto', py: 1 }}>
          {showHint && (
            <Box sx={{ px: 3, py: 3, textAlign: 'center' }}>
              <Typography sx={{ fontSize: 13, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                {t('search.hint')}
              </Typography>
            </Box>
          )}

          {showEmpty && (
            <Box sx={{ px: 3, py: 3, textAlign: 'center' }}>
              <Typography sx={{ fontSize: 13, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                {t('search.noResults', { query })}
              </Typography>
            </Box>
          )}

          {filteredLeads.length > 0 && (
            <>
              <SectionLabel label={t('search.leads')} count={filteredLeads.length} />
              {filteredLeads.map((lead, idx) => (
                <ResultRow
                  key={lead.id}
                  label={`${lead.first_name} ${lead.last_name}`}
                  sub={[lead.email, lead.company].filter(Boolean).join(' · ')}
                  badge={lead.status}
                  badgeColor={LEAD_STATUS_COLOR[lead.status]}
                  active={activeIdx === idx}
                  onClick={() => { navigate(`/leads/${lead.id}`); onClose(); }}
                />
              ))}
            </>
          )}

          {filteredDeals.length > 0 && (
            <>
              <SectionLabel label={t('search.deals')} count={filteredDeals.length} />
              {filteredDeals.map((deal, idx) => {
                const globalIdx = filteredLeads.length + idx;
                return (
                  <ResultRow
                    key={deal.id}
                    label={deal.title}
                    sub={[deal.company, deal.contact_name].filter(Boolean).join(' · ')}
                    badge={deal.status}
                    badgeColor={DEAL_STATUS_COLOR[deal.status]}
                    active={activeIdx === globalIdx}
                    onClick={() => { navigate('/deals'); onClose(); }}
                  />
                );
              })}
            </>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{
          px: 2, py: 1, borderTop: `1px solid ${C.border}`,
          display: 'flex', alignItems: 'center', gap: 2,
          bgcolor: C.bg,
        }}>
          {[
            { key: '↑↓', label: t('search.keyNavigate') },
            { key: '↵', label: t('search.keySelect') },
            { key: 'Esc', label: t('search.keyClose') },
          ].map(({ key, label }) => (
            <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box sx={{
                px: '5px', py: '1px', borderRadius: '4px',
                border: `1px solid ${C.border}`, bgcolor: '#fff',
                fontSize: 10, fontWeight: 600, fontFamily: 'Inter, sans-serif', color: C.muted,
              }}>
                {key}
              </Box>
              <Typography sx={{ fontSize: 11, color: C.muted, fontFamily: 'Inter, sans-serif' }}>
                {label}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </>
  );
}
