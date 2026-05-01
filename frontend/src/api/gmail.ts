import type { EmailMessage, GmailAuthStatus, GmailAuthUrl, SendEmailPayload } from '../types/email';
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
};
