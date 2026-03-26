import { apiClient } from "../client";
import { useAuthStore } from "../../store/useAuthStore";

test('attaches Authorization header when token is present', async () => {
  // Directly set auth state — avoids making a real network call to /auth/login
  useAuthStore.setState({ isAuthenticated: true, accessToken: 'test-jwt-token-123' });

  let capturedConfig: any;
  const id = apiClient.interceptors.request.use((config) => {
    capturedConfig = config;
    return config;
  });

  try {
    await apiClient.get('/health');
  } catch {
    // Ignore network errors — we only care about the request config
  }

  expect(capturedConfig.headers.Authorization).toMatch(/^Bearer .+/);

  apiClient.interceptors.request.eject(id);
  useAuthStore.getState().logout();
});

test('omits Authorization header when no token is present', async () => {
  useAuthStore.setState({ isAuthenticated: false, accessToken: null });

  let capturedConfig: any;
  const id = apiClient.interceptors.request.use((config) => {
    capturedConfig = config;
    return config;
  });

  try {
    await apiClient.get('/health');
  } catch {
    // Ignore network errors
  }

  expect(capturedConfig.headers.Authorization).toBeUndefined();

  apiClient.interceptors.request.eject(id);
});
