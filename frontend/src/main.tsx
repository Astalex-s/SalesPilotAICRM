import * as Sentry from '@sentry/react';
import React from 'react';
import ReactDOM from 'react-dom/client';
import './i18n';
import App from './App';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN as string | undefined,
  environment: (import.meta.env.VITE_APP_ENV as string | undefined) ?? 'development',
  release: import.meta.env.VITE_APP_VERSION as string | undefined,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.05,
  replaysOnErrorSampleRate: 1.0,
  enabled: !!import.meta.env.VITE_SENTRY_DSN,
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<SentryFallback />}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>,
);

function SentryFallback() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', fontFamily: 'Inter, sans-serif', gap: 16 }}>
      <h2 style={{ margin: 0, color: 'text.primary' }}>Something went wrong</h2>
      <p style={{ margin: 0, color: '#6B7280' }}>The error has been reported automatically.</p>
      <button onClick={() => window.location.reload()} style={{ padding: '8px 20px', background: '#00A8E8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14 }}>
        Reload page
      </button>
    </div>
  );
}
