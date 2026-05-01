import type { AnonymizeLeadResult, DeleteUserDataResult, GdprAuditLog } from '../types/gdpr';
import axiosInstance from './axiosInstance';

export const gdprApi = {
  deleteUserData: async (userId: string): Promise<DeleteUserDataResult> => {
    const { data } = await axiosInstance.post<DeleteUserDataResult>(
      `/gdpr/users/${userId}/delete`,
    );
    return data;
  },

  anonymizeLead: async (leadId: string): Promise<AnonymizeLeadResult> => {
    const { data } = await axiosInstance.post<AnonymizeLeadResult>(
      `/gdpr/leads/${leadId}/anonymize`,
    );
    return data;
  },

  getAuditLog: async (limit = 100, offset = 0): Promise<GdprAuditLog> => {
    const { data } = await axiosInstance.get<GdprAuditLog>('/gdpr/audit-log', {
      params: { limit, offset },
    });
    return data;
  },
};
