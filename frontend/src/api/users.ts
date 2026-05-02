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

export async function updateProfile(firstName: string, lastName: string): Promise<User> {
  const { data } = await axiosInstance.patch<User>('/users/me', {
    first_name: firstName,
    last_name: lastName,
  });
  return data;
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await axiosInstance.post('/users/me/password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
}
