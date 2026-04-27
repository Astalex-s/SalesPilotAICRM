import axiosInstance from './axiosInstance';
import type { User, UserRole } from '../types/auth';

export async function listUsers(): Promise<User[]> {
  const { data } = await axiosInstance.get<User[]>('/users');
  return data;
}

export async function updateUserRole(userId: string, role: UserRole): Promise<User> {
  const { data } = await axiosInstance.patch<User>(`/users/${userId}/role`, { role });
  return data;
}
