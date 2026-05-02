import axiosInstance from './axiosInstance';
import type { DealAttachment } from '../types/attachment';

export const attachmentsApi = {
  list: async (dealId: string): Promise<DealAttachment[]> => {
    const { data } = await axiosInstance.get<DealAttachment[]>(`/deals/${dealId}/attachments`);
    return data;
  },

  upload: async (dealId: string, file: File): Promise<DealAttachment> => {
    const form = new FormData();
    form.append('file', file);
    const { data } = await axiosInstance.post<DealAttachment>(
      `/deals/${dealId}/attachments`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    );
    return data;
  },

  delete: async (dealId: string, attachmentId: string): Promise<void> => {
    await axiosInstance.delete(`/deals/${dealId}/attachments/${attachmentId}`);
  },

  downloadUrl: (dealId: string, attachmentId: string): string =>
    `/api/v1/deals/${dealId}/attachments/${attachmentId}/download`,
};
