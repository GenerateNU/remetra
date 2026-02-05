// This would be in src/api/client.ts
import axios from 'axios';
import type { Chocolate, ChocolateFilters } from './chocolates'

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data ?? error.message);
    return Promise.reject(error);
  }
);

// This would be in src/api/endpoints.ts
export const api = {
  getChocolates: async (filters?: ChocolateFilters): Promise<Chocolate[]> => {
    const params = new URLSearchParams();
    
    if (filters?.min_price !== undefined) {
      params.append('min_price', filters.min_price.toString());
    }
    if (filters?.max_price !== undefined) {
      params.append('max_price', filters.max_price.toString());
    }
    if (filters?.in_stock_only) {
      params.append('in_stock_only', 'true');
    }

    const { data } = await apiClient.get<Chocolate[]>('/chocolates/', { params });
    return data;
  },
};