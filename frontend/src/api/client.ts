import axios, { AxiosInstance } from 'axios';

// Use EXPO_PUBLIC_API_URL when provided (set in README-DEV / .env for dev);
// fallback to localhost so the app talks to the locally running FastAPI server.
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// --- Auth token handling (temporary hard-coded token for acceptance criteria) ---
// In future this will be read from secure storage and managed by auth state.
let authToken: string = 'HARDCODED_JWT'; // hard-code JWT for now

// Request interceptor — attaches Bearer token when available
apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers = config.headers ?? {};
    config.headers['Authorization'] = `Bearer ${authToken}`;
  }
  return config;
});

// Callback to handle unauthenticated state - set this from your auth context/store
let onUnauthenticated: (() => void) | null = null;

export const setOnUnauthenticated = (callback: () => void) => {
  onUnauthenticated = callback;
};

// Attach a simple response interceptor for centralized error logging
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Keep the log concise but useful during development

    // Handle 401: Unauthorized
    if (error.response?.status === 401) {
      onUnauthenticated?.();
    }

    // (backend error payloads will appear in error.response.data)
    // eslint-disable-next-line no-console
    console.error('API Error:', error.response?.data ?? error.message);
    return Promise.reject(error);
  }
);