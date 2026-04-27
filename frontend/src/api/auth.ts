import axiosInstance from './axiosInstance';
import type { LoginPayload, RegisterPayload, TokenResponse, User } from '../types/auth';

export async function register(payload: RegisterPayload): Promise<User> {
  const { data } = await axiosInstance.post<User>('/auth/register', payload);
  return data;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await axiosInstance.post<TokenResponse>('/auth/login', payload);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await axiosInstance.get<User>('/auth/me');
  return data;
}
