import { apiClient } from './client';

export interface RagQueryPayload {
  query: string;
  context_limit: number;
}

export interface RagQueryResponse {
  answer: string;
  sources?: Array<{ id: string; text: string }>; 
  metadata?: Record<string, unknown>;
}

export interface RagClearHistoryResponse {
  detail?: string;
}

export class RagError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RagError';
  }
}

export const ragService = {
  // POST /rag/query
  async query(payload: RagQueryPayload): Promise<RagQueryResponse> {
    try {
      const { data } = await apiClient.post<RagQueryResponse>('/rag/query', payload);
      return data;
    } catch (err: any) {
      throw new RagError(err?.response?.data?.detail ?? 'Failed to query RAG service');
    }
  },

  // DELETE /rag/history
  async clearHistory(): Promise<RagClearHistoryResponse> {
    try {
      const { data } = await apiClient.delete<RagClearHistoryResponse>('/rag/history');
      return data;
    } catch (err: any) {
      throw new RagError(err?.response?.data?.detail ?? 'Failed to clear RAG history');
    }
  },
};
