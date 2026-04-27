import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10_000,
});

// Attach JWT token from localStorage on every request
axiosInstance.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('crm-auth');
    if (raw) {
      const parsed = JSON.parse(raw) as { state?: { token?: string } };
      const token = parsed?.state?.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch {
    // ignore parse errors
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      try {
        localStorage.removeItem('crm-auth');
      } catch {
        // ignore
      }
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    const message: string =
      error.response?.data?.detail ?? error.message ?? 'Unknown error';
    return Promise.reject(new Error(message));
  },
);

export default axiosInstance;
