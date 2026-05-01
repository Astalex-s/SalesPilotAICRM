import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import AIAssistantPage from './pages/AIAssistantPage';
import SettingsPage from './pages/SettingsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import GdprPage from './pages/GdprPage';
import GmailPage from './pages/GmailPage';
import TelegramPage from './pages/TelegramPage';
import DashboardPage from './pages/DashboardPage';
import DealsPage from './pages/DealsPage';
import LeadDetailPage from './pages/LeadDetailPage';
import LeadsPage from './pages/LeadsPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import LoginPage from './pages/LoginPage';
import PipelinePage from './pages/PipelinePage';
import RegisterPage from './pages/RegisterPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import UsersPage from './pages/UsersPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#9c27b0' },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="leads" element={<LeadsPage />} />
              <Route path="leads/:leadId" element={<LeadDetailPage />} />
              <Route path="deals" element={<DealsPage />} />
              <Route path="pipeline/:pipelineId" element={<PipelinePage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="gmail" element={<GmailPage />} />
              <Route path="telegram" element={<TelegramPage />} />
              <Route path="gdpr" element={<GdprPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="ai-assistant" element={<AIAssistantPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
