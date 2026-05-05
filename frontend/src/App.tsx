import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { useMemo } from 'react';
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
import CalendarPage from './pages/CalendarPage';
import TasksPage from './pages/TasksPage';
import UsersPage from './pages/UsersPage';
import { useSettingsStore } from './store/useSettingsStore';

function buildTheme(dark: boolean) {
  return createTheme({
    palette: {
      mode: dark ? 'dark' : 'light',
      primary:   { main: '#00A8E8' },
      secondary: { main: '#FF6B35' },
      ...(dark ? {
        background: { default: '#0F1724', paper: '#172133' },
        text:       { primary: '#E2EAF4', secondary: '#7F93AC' },
        divider:    '#243448',
      } : {
        background: { default: '#F7F9FC', paper: '#FFFFFF' },
        text:       { primary: '#191C1E', secondary: '#5E6E82' },
        divider:    '#E8EFF7',
      }),
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: { fontFamily: 'Inter, sans-serif' },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: 'none' },
        },
      },
    },
  });
}

export default function App() {
  const darkMode = useSettingsStore((s) => s.darkMode);
  const theme = useMemo(() => buildTheme(darkMode), [darkMode]);

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
              <Route path="tasks" element={<TasksPage />} />
              <Route path="calendar" element={<CalendarPage />} />
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
