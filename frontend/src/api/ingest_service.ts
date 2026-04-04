import { apiClient } from './client';

export interface IngestPdfResponse {
  [key: string]: unknown;
}

export interface IngestFolderResponse {
  message?: string;
  sources_ingested?: string[];
}

export class IngestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'IngestError';
  }
}

export const ingestService = {
  // POST /ingest/pdf
  async ingestPdf(file: File): Promise<IngestPdfResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await apiClient.post<IngestPdfResponse>('/ingest/pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    } catch (err: any) {
      throw new IngestError(err?.response?.data?.detail ?? 'Failed to ingest PDF');
    }
  },

  // POST /ingest/folder
  async ingestFolder(): Promise<IngestFolderResponse> {
    try {
      const { data } = await apiClient.post<IngestFolderResponse>('/ingest/folder');
      return data;
    } catch (err: any) {
      throw new IngestError(err?.response?.data?.detail ?? 'Failed to ingest folder');
    }
  },
};
