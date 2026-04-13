
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService, LoginPayload, RegisterPayload } from '../api/auth_service';
import { useBankStore } from './bankStore';

interface UserProfile {
  id: string | null;
  email: string | null;
  name: string | null;
  avatarUrl: string | null;
}

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  hasCompletedOnboarding: boolean;
  user: UserProfile;
}

interface AuthActions {
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  completeOnboarding: () => void;
  updateUserProfile: (profile: Partial<UserProfile>) => void;
}

type AuthStore = AuthState & AuthActions;

const initialUserProfile: UserProfile = {
  id: null,
  email: null,
  name: null,
  avatarUrl: null,
};

const initialState: AuthState = {
  isAuthenticated: false,
  accessToken: null,
  hasCompletedOnboarding: false,
  user: initialUserProfile,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      login: async (payload) => {
        const response = await authService.login(payload);
        // Set token first so the getMe interceptor can attach it
        set({
          isAuthenticated: true,
          accessToken: response.access_token,
          user: { ...initialUserProfile, name: response.username },
        });
        const me = await authService.getMe();
        set((state) => ({
          user: { ...state.user, email: me.email },
        }));
      },

      register: async (payload) => {
        const response = await authService.register(payload);
        set({
          isAuthenticated: true,
          accessToken: response.access_token,
          user: { ...initialUserProfile, name: response.username, email: payload.email },
        });
      },

      logout: () => {
        useBankStore.getState().clearBank();
        set({
          isAuthenticated: false,
          accessToken: null,
          hasCompletedOnboarding: false,
          user: initialUserProfile,
        });
      },

      completeOnboarding: () =>
        set({ hasCompletedOnboarding: true }),

      updateUserProfile: (profile) =>
        set((state) => ({
          user: { ...state.user, ...profile },
        })),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        accessToken: state.accessToken,
        hasCompletedOnboarding: state.hasCompletedOnboarding,
        user: state.user,
      }),
    }
  )
);

// // Selector hooks
// export const useIsAuthenticated = () => useAuthStore((s) => s.isAuthenticated);
// export const useaccessToken = () => useAuthStore((s) => s.accessToken);
// export const useHasCompletedOnboarding = () => useAuthStore((s) => s.hasCompletedOnboarding);
// export const useUser = () => useAuthStore((s) => s.user);