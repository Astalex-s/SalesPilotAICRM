import type { TelegramStatus, TelegramWebhookSetResult } from '../types/telegram';
import axiosInstance from './axiosInstance';

export const telegramApi = {
  getStatus: async (): Promise<TelegramStatus> => {
    const { data } = await axiosInstance.get<TelegramStatus>('/telegram/status');
    return data;
  },

  setWebhook: async (url: string, secretToken?: string): Promise<TelegramWebhookSetResult> => {
    const { data } = await axiosInstance.post<TelegramWebhookSetResult>('/telegram/set-webhook', {
      url,
      ...(secretToken ? { secret_token: secretToken } : {}),
    });
    return data;
  },
};
