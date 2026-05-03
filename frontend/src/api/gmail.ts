import type {
  EmailMessage,
  EmailSyncResult,
  EmailThreadDetail,
  EmailThreadSummary,
  GmailAuthStatus,
  GmailAuthUrl,
  SendEmailPayload,
} from '../types/email';
import axiosInstance from './axiosInstance';

export const gmailApi = {
  getAuthStatus: async (): Promise<GmailAuthStatus> => {
    const { data } = await axiosInstance.get<GmailAuthStatus>('/auth/gmail/status');
    return data;
  },

  getAuthUrl: async (): Promise<GmailAuthUrl> => {
    const { data } = await axiosInstance.get<GmailAuthUrl>('/auth/gmail');
    return data;
  },

  /** Список писем из локальной БД (без Gmail API) */
  listEmails: async (limit = 100, offset = 0): Promise<EmailMessage[]> => {
    const { data } = await axiosInstance.get<EmailMessage[]>('/emails/stored', {
      params: { limit, offset },
    });
    return data;
  },

  /** Триггер фоновой синхронизации через Celery */
  triggerSync: async (query = '', maxResults = 100): Promise<EmailSyncResult> => {
    const { data } = await axiosInstance.post<EmailSyncResult>('/emails/sync', null, {
      params: { query, max_results: maxResults },
    });
    return data;
  },

  /** Устаревший метод — оставлен для обратной совместимости */
  fetchEmails: async (query = '', maxResults = 50): Promise<EmailMessage[]> => {
    const { data } = await axiosInstance.get<EmailMessage[]>('/emails', {
      params: { query, max_results: maxResults },
    });
    return data;
  },

  sendEmail: async (payload: SendEmailPayload): Promise<EmailMessage> => {
    const { data } = await axiosInstance.post<EmailMessage>('/emails/send', payload);
    return data;
  },

  linkToLead: async (emailId: string, leadId: string): Promise<EmailMessage> => {
    const { data } = await axiosInstance.post<EmailMessage>(
      `/emails/${emailId}/link-lead`,
      null,
      { params: { lead_id: leadId } },
    );
    return data;
  },

  listThreads: async (): Promise<EmailThreadSummary[]> => {
    const { data } = await axiosInstance.get<EmailThreadSummary[]>('/emails/threads');
    return data;
  },

  getThread: async (threadId: string): Promise<EmailThreadDetail> => {
    const { data } = await axiosInstance.get<EmailThreadDetail>(`/emails/threads/${threadId}`);
    return data;
  },
};
