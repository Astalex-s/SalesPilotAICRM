import axiosInstance from './axiosInstance';
import type {
  ForgotPasswordPayload,
  LoginPayload,
  RegisterPayload,
  ResetPasswordPayload,
  TokenResponse,
  User,
} from '../types/auth';

export async function register(payload: RegisterPayload): Promise<User> {
  const { data } = await axiosInstance.post<User>('/auth/register', payload);
  return data;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await axiosInstance.post<TokenResponse>('/auth/login', payload);
  return data;
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  const { data } = await axiosInstance.post<TokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  return data;
}

export async function forgotPassword(payload: ForgotPasswordPayload): Promise<void> {
  await axiosInstance.post('/auth/forgot-password', payload);
}

export async function resetPassword(payload: ResetPasswordPayload): Promise<void> {
  await axiosInstance.post('/auth/reset-password', payload);
}

export async function getMe(): Promise<User> {
  const { data } = await axiosInstance.get<User>('/auth/me');
  return data;
}
