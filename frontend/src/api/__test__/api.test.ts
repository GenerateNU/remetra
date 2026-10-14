import { apiClient } from "../client";
import { setClerkTokenGetter } from "../clerkToken";

test('attaches Authorization header when a Clerk token is available', async () => {
  setClerkTokenGetter(async () => 'test-jwt-token-123');

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

  expect(capturedConfig.headers.Authorization).toBe('Bearer test-jwt-token-123');

  apiClient.interceptors.request.eject(id);
  setClerkTokenGetter(null);
});

test('omits Authorization header when no Clerk token is available', async () => {
  setClerkTokenGetter(null);

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
