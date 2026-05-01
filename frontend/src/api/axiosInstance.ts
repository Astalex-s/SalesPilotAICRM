import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const axiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10_000,
});

function getStoredAuth(): { token?: string; refreshToken?: string } {
  try {
    const raw = localStorage.getItem('crm-auth');
    if (raw) {
      const parsed = JSON.parse(raw) as { state?: { token?: string; refreshToken?: string } };
      return {
        token: parsed?.state?.token,
        refreshToken: parsed?.state?.refreshToken ?? undefined,
      };
    }
  } catch {
    // ignore
  }
  return {};
}

// Attach JWT token from localStorage on every request
axiosInstance.interceptors.request.use((config) => {
  const { token } = getStoredAuth();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let _isRefreshing = false;
let _refreshQueue: Array<(token: string) => void> = [];

function processQueue(newToken: string) {
  _refreshQueue.forEach((resolve) => resolve(newToken));
  _refreshQueue = [];
}

function clearAuthAndRedirect() {
  try {
    localStorage.removeItem('crm-auth');
  } catch {
    // ignore
  }
  if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
    window.location.href = '/login';
  }
}

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !original._retry) {
      const { refreshToken } = getStoredAuth();

      // No refresh token — bail out immediately
      if (!refreshToken) {
        clearAuthAndRedirect();
        const message: string = error.response?.data?.detail ?? error.message ?? 'Unknown error';
        return Promise.reject(new Error(message));
      }

      if (_isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve) => {
          _refreshQueue.push((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(axiosInstance(original));
          });
        });
      }

      original._retry = true;
      _isRefreshing = true;

      try {
        // Call refresh directly (bypass interceptor to avoid infinite loop)
        const { data } = await axios.post<{ access_token: string; refresh_token: string }>(
          '/api/v1/auth/refresh',
          { refresh_token: refreshToken },
        );

        // Persist new tokens into localStorage (Zustand's persist format)
        try {
          const raw = localStorage.getItem('crm-auth');
          const parsed = raw ? (JSON.parse(raw) as { state?: Record<string, unknown> }) : { state: {} };
          parsed.state = {
            ...parsed.state,
            token: data.access_token,
            refreshToken: data.refresh_token,
          };
          localStorage.setItem('crm-auth', JSON.stringify(parsed));
        } catch {
          // ignore
        }

        processQueue(data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return axiosInstance(original);
      } catch {
        clearAuthAndRedirect();
        return Promise.reject(new Error('Session expired'));
      } finally {
        _isRefreshing = false;
      }
    }

    const message: string = error.response?.data?.detail ?? error.message ?? 'Unknown error';
    return Promise.reject(new Error(message));
  },
);

export default axiosInstance;
