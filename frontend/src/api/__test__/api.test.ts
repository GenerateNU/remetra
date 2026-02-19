import { apiClient } from "../client";
import { useAuthStore } from "../../store/useAuthStore";

test('attach JWT middleware', async () => {
  // Set up auth state before making the request
  useAuthStore.getState().login('test-jwt-token-123', {
    id: 'user-1',
    email: 'test@example.com',
  });

  let capturedConfig: any;
  // Add temporary intercept middleware to capture the request info
  const id = apiClient.interceptors.request.use((config) => {
    capturedConfig = config;
    return config;
  });

  try {
    await apiClient.get('/health');
  } catch {
    // Ignore network errors in test
  }

  expect(capturedConfig.headers.Authorization).toMatch(/^Bearer .+/);

  // Clean up the spy interceptor
  apiClient.interceptors.request.eject(id);

  // Clean up auth state
  useAuthStore.getState().logout();
});

// future to ensure no authorization header if no bearer token provided