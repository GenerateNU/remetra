import { apiClient } from "../client";

test('attach JWT middleware', async () => {
  let capturedConfig: any;
  // Add temporary intercept middleware to capture the request info
  const id = apiClient.interceptors.request.use((config) => {
    capturedConfig = config;
    return config;
  });

  try {
    await apiClient.get('/health');
  } catch {

  }

  expect(capturedConfig.headers.Authorization).toMatch(/^Bearer .+/);

  // Clean up the spy interceptor
  apiClient.interceptors.request.eject(id);
})

// future to ensure no authorization header if no bearer token provided