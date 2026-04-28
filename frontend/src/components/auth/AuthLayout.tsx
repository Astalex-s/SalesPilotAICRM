import { Box, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

/* ── Abstract SVG illustration (dark navy + cyan + coral-orange) ───────────── */
const AuthIllustration = () => (
  <svg
    viewBox="0 0 900 900"
    xmlns="http://www.w3.org/2000/svg"
    style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
    preserveAspectRatio="xMidYMid slice"
  >
    <defs>
      <radialGradient id="glowMain" cx="55%" cy="65%" r="55%">
        <stop offset="0%" stopColor="#00A8E8" stopOpacity="0.22" />
        <stop offset="100%" stopColor="#00A8E8" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="glowTop" cx="25%" cy="30%" r="40%">
        <stop offset="0%" stopColor="#00A8E8" stopOpacity="0.12" />
        <stop offset="100%" stopColor="#00A8E8" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="barsGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#00A8E8" stopOpacity="0.35" />
        <stop offset="100%" stopColor="#00A8E8" stopOpacity="0" />
      </radialGradient>
      <linearGradient id="barA" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#00C8FF" stopOpacity="0.95" />
        <stop offset="100%" stopColor="#00A8E8" stopOpacity="0.25" />
      </linearGradient>
      <linearGradient id="barB" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#00A8E8" stopOpacity="0.80" />
        <stop offset="100%" stopColor="#006699" stopOpacity="0.20" />
      </linearGradient>
      <filter id="softBlur" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="6" />
      </filter>
      <filter id="lineGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" />
      </filter>
    </defs>

    {/* Base */}
    <rect width="900" height="900" fill="#0D2144" />

    {/* Dot grid */}
    <pattern id="dotgrid" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.5" fill="#ffffff" opacity="0.07" />
    </pattern>
    <rect width="900" height="900" fill="url(#dotgrid)" />

    {/* Ambient glows */}
    <rect width="900" height="900" fill="url(#glowMain)" />
    <rect width="900" height="900" fill="url(#glowTop)" />

    {/* Large depth circle (navy on navy) */}
    <circle cx="720" cy="180" r="380" fill="none" stroke="#162E5C" strokeWidth="90" opacity="0.7" />
    <circle cx="720" cy="180" r="250" fill="none" stroke="#1A3868" strokeWidth="1.5" opacity="0.5" />

    {/* Flowing cyan arcs */}
    <path d="M-60 680 C 120 450, 400 620, 620 480 C 780 370, 860 420, 960 380"
      stroke="#00A8E8" strokeWidth="1.8" fill="none" opacity="0.35" />
    <path d="M-60 720 C 100 510, 360 660, 580 530 C 750 420, 850 460, 960 430"
      stroke="#00C8FF" strokeWidth="1" fill="none" opacity="0.2" />
    <path d="M0 600 C 200 380, 480 560, 680 420 C 820 320, 880 350, 960 320"
      stroke="#00A8E8" strokeWidth="2.5" fill="none" opacity="0.25" />
    <path d="M-100 550 C 160 300, 440 500, 660 360 C 800 270, 880 300, 980 260"
      stroke="#00DFFF" strokeWidth="1" fill="none" opacity="0.15" />

    {/* Secondary smaller arc top-right */}
    <path d="M500 -50 C 650 100, 800 50, 960 150"
      stroke="#00A8E8" strokeWidth="1.5" fill="none" opacity="0.2" />

    {/* Bar chart glow layer */}
    <rect x="270" y="470" width="360" height="260" fill="url(#barsGlow)" filter="url(#softBlur)" opacity="0.6" />

    {/* Bar chart bars — 8 bars, varying heights, upward trend */}
    {[
      { x: 290, h: 160, y: 570 },
      { x: 330, h: 200, y: 530 },
      { x: 370, h: 140, y: 590 },
      { x: 410, h: 215, y: 515 },
      { x: 450, h: 175, y: 555 },
      { x: 490, h: 235, y: 495 },
      { x: 530, h: 195, y: 535 },
      { x: 570, h: 260, y: 470 },
    ].map(({ x, h, y }, i) => (
      <g key={i}>
        {/* Glow shadow */}
        <rect x={x} y={y} width="26" height={h} rx="4"
          fill="#00A8E8" filter="url(#softBlur)" opacity="0.3" />
        {/* Bar */}
        <rect x={x} y={y} width="26" height={h} rx="4"
          fill={i % 2 === 0 ? 'url(#barA)' : 'url(#barB)'} />
      </g>
    ))}

    {/* Trend line over bars */}
    <polyline
      points="303,550 343,510 383,570 423,494 463,533 503,474 543,514 583,450"
      stroke="#00EEFF" strokeWidth="2.5" fill="none"
      strokeLinecap="round" strokeLinejoin="round" opacity="0.95" />
    {/* Trend line glow */}
    <polyline
      points="303,550 343,510 383,570 423,494 463,533 503,474 543,514 583,450"
      stroke="#00EEFF" strokeWidth="8" fill="none"
      strokeLinecap="round" strokeLinejoin="round"
      filter="url(#lineGlow)" opacity="0.3" />

    {/* Baseline for chart */}
    <line x1="275" y1="730" x2="625" y2="730"
      stroke="rgba(255,255,255,0.12)" strokeWidth="1" />

    {/* Coral-orange accents */}
    <circle cx="160" cy="220" r="5.5" fill="#FF6B35" opacity="0.75" />
    <circle cx="210" cy="380" r="3.5" fill="#FF6B35" opacity="0.6" />
    <circle cx="110" cy="490" r="4" fill="#FF6B35" opacity="0.65" />
    <circle cx="760" cy="620" r="5" fill="#FF6B35" opacity="0.55" />
    <circle cx="830" cy="420" r="3" fill="#FF6B35" opacity="0.7" />
    <circle cx="700" cy="730" r="4.5" fill="#FF6B35" opacity="0.5" />
    <circle cx="260" cy="160" r="3" fill="#FF6B35" opacity="0.65" />
    <circle cx="620" cy="200" r="4" fill="#FF6B35" opacity="0.55" />
    <circle cx="80" cy="340" r="2.5" fill="#FF6B35" opacity="0.6" />
    <circle cx="850" cy="560" r="3" fill="#FF6B35" opacity="0.5" />

    {/* Small coral triangles */}
    <polygon points="185,320 195,303 205,320" fill="#FF6B35" opacity="0.45" />
    <polygon points="750,560 762,542 774,560" fill="#FF6B35" opacity="0.4" />

    {/* Cyan data dots (small) */}
    <circle cx="175" cy="620" r="2" fill="#00A8E8" opacity="0.55" />
    <circle cx="250" cy="700" r="1.5" fill="#00A8E8" opacity="0.45" />
    <circle cx="810" cy="310" r="2" fill="#00A8E8" opacity="0.55" />
    <circle cx="860" cy="490" r="1.5" fill="#00A8E8" opacity="0.4" />
    <circle cx="140" cy="760" r="2" fill="#00A8E8" opacity="0.4" />
  </svg>
);

/* ── Shared input style ────────────────────────────────────────────────────── */
export const inputSx = {
  width: '100%',
  height: 44,
  bgcolor: '#FFFFFF',
  border: '1px solid #BDC8D1',
  borderRadius: '8px',
  color: '#171C20',
  fontSize: 14,
  px: '14px',
  outline: 'none',
  boxSizing: 'border-box' as const,
  fontFamily: 'Inter, sans-serif',
  transition: 'border-color 0.2s, box-shadow 0.2s',
  '&:focus': {
    borderColor: '#00A8E8',
    boxShadow: '0 0 0 3px rgba(0,168,232,0.18)',
  },
  '&::placeholder': { color: '#9EAAB5' },
};

/* ── Layout component ─────────────────────────────────────────────────────── */
interface AuthLayoutProps {
  activeTab: 'login' | 'register';
  children: React.ReactNode;
}

export default function AuthLayout({ activeTab, children }: AuthLayoutProps) {
  const navigate = useNavigate();

  return (
    <Box sx={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden', fontFamily: 'Inter, sans-serif' }}>

      {/* ── LEFT: illustration (75%) ──────────────────────────────────────── */}
      <Box sx={{
        display: { xs: 'none', lg: 'flex' },
        width: '75%',
        position: 'relative',
        bgcolor: '#0D2144',
        flexDirection: 'column',
        justifyContent: 'space-between',
        p: 5,
        overflow: 'hidden',
      }}>
        <AuthIllustration />

        {/* Logo */}
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box
            component="img"
            src="/logo.png"
            alt="Sales Pilot AI CRM"
            sx={{ height: 48, display: 'block' }}
          />
        </Box>

        {/* Tagline */}
        <Typography sx={{
          position: 'relative',
          zIndex: 1,
          color: 'rgba(255,255,255,0.82)',
          fontSize: 20,
          fontWeight: 300,
          fontFamily: 'Inter, sans-serif',
          letterSpacing: '0.01em',
          mb: 1,
        }}>
          Close more deals.{' '}
          <Box component="span" sx={{ color: '#00A8E8', fontWeight: 500 }}>Faster.</Box>
        </Typography>
      </Box>

      {/* ── RIGHT: form panel (25%) ───────────────────────────────────────── */}
      <Box sx={{
        width: { xs: '100%', lg: '25%' },
        minWidth: { lg: 320 },
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        bgcolor: 'rgba(255,255,255,0.97)',
        backdropFilter: 'blur(20px)',
        borderLeft: '1px solid #E8EFF7',
        boxShadow: '-12px 0 40px rgba(13,33,68,0.1)',
        zIndex: 2,
        overflowY: 'auto',
        px: { xs: 3, sm: 4 },
        py: 4,
      }}>
        <Box sx={{ width: '100%', maxWidth: 360, mx: 'auto' }}>

          {/* Tabs */}
          <Box sx={{ display: 'flex', borderBottom: '1px solid #D6DAE0', mb: 4 }}>
            {(['login', 'register'] as const).map((tab) => {
              const active = activeTab === tab;
              const label = tab === 'login' ? 'Sign In' : 'Register';
              return (
                <Box
                  key={tab}
                  component="button"
                  onClick={() => navigate(tab === 'login' ? '/login' : '/register')}
                  sx={{
                    flex: 1,
                    pb: 1.5,
                    textAlign: 'center',
                    fontSize: 14,
                    fontWeight: active ? 700 : 400,
                    fontFamily: 'Inter, sans-serif',
                    color: active ? '#00A8E8' : '#6E7881',
                    border: 'none',
                    background: 'none',
                    cursor: active ? 'default' : 'pointer',
                    borderBottom: active ? '2px solid #00A8E8' : '2px solid transparent',
                    mb: '-1px',
                    transition: 'color 0.15s',
                    '&:hover': { color: active ? '#00A8E8' : '#171C20' },
                  }}
                >
                  {label}
                </Box>
              );
            })}
          </Box>

          {/* Form content injected by page */}
          {children}
        </Box>
      </Box>
    </Box>
  );
}
