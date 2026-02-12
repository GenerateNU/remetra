import axios, { AxiosInstance } from 'axios';

// Use EXPO_PUBLIC_API_URL when provided (set in README-DEV / .env for dev);
// fallback to localhost so the app talks to the locally running FastAPI server.
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach a simple response interceptor for centralized error logging
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Keep the log concise but useful during development
    // (backend error payloads will appear in error.response.data)
    // eslint-disable-next-line no-console
    console.error('API Error:', error.response?.data ?? error.message);
    return Promise.reject(error);
  }
);
