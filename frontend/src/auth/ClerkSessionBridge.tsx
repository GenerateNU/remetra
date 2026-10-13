import { useEffect } from 'react';
import { useAuth } from '@clerk/expo';
import { setOnUnauthenticated } from '../api/client';
import { setClerkTokenGetter } from '../api/clerkToken';
import { useAuthStore } from '../store/useAuthStore';

const isClerkOfflineError = (error: unknown) =>
  typeof error === 'object' &&
  error !== null &&
  'code' in error &&
  (error as { code?: string }).code === 'clerk_offline';

export function ClerkSessionBridge() {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  useEffect(() => {
    setClerkTokenGetter(async () => {
      try {
        return await getToken();
      } catch (error) {
        if (isClerkOfflineError(error)) throw error;
        return null;
      }
    });
    return () => setClerkTokenGetter(null);
  }, [getToken]);

  useEffect(() => {
    setOnUnauthenticated(() => {
      useAuthStore.getState().logout();
    });
  }, []);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      useAuthStore.getState().clearLocal();
      return;
    }
    useAuthStore.getState().setSignedIn();
    useAuthStore.getState().refreshProfile().catch(() => {
      // Profile refresh can fail before the local row exists. Navigation still
      // follows the Clerk session; the next /auth/me call retries.
    });
  }, [isLoaded, isSignedIn]);

  return null;
}
