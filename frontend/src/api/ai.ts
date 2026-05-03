import { type AiTone, type DealForecast, type GeneratedEmail, type LeadScore, type LostDealsAnalysis, type NextBestAction, type PipelineDigest } from '../types/ai';
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

  forecastDeal: async (dealId: string): Promise<DealForecast> => {
    const { data } = await axiosInstance.post<DealForecast>(
      `/ai/deals/${dealId}/forecast`,
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

  analyzeLostDeals: async (): Promise<LostDealsAnalysis> => {
    const { data } = await axiosInstance.post<LostDealsAnalysis>('/ai/deals/lost-analysis');
    return data;
  },

  pipelineWeeklyDigest: async (pipelineId: string): Promise<PipelineDigest> => {
    const { data } = await axiosInstance.get<PipelineDigest>(
      `/ai/pipeline/${pipelineId}/weekly-digest`,
    );
    return data;
  },
};
