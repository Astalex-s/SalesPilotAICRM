import { type AiTone, type GeneratedEmail, type LeadScore, type NextBestAction } from '../types/ai';
import axiosInstance from './axiosInstance';

export const aiApi = {
  scoreLead: async (leadId: string): Promise<LeadScore> => {
    const { data } = await axiosInstance.post<LeadScore>(
      `/ai/leads/${leadId}/score`,
    );
    return data;
  },

  nextBestAction: async (leadId: string): Promise<NextBestAction> => {
    const { data } = await axiosInstance.post<NextBestAction>(
      `/ai/lead/${leadId}/next-action`,
    );
    return data;
  },

  generateEmail: async (
    leadId: string,
    tone: AiTone = 'friendly',
    extraContext?: string,
  ): Promise<GeneratedEmail> => {
    const { data } = await axiosInstance.post<GeneratedEmail>(
      `/ai/leads/${leadId}/generate-email`,
      null,
      { params: { tone, ...(extraContext ? { extra_context: extraContext } : {}) } },
    );
    return data;
  },
};
