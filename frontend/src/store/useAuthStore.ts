
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService, LoginPayload, MeResponse, RegisterPayload } from '../api/auth_service';
import { useBankStore } from './bankStore';

interface UserProfile {
  id: string | null;
  email: string | null;
  name: string | null;
  avatarUrl: string | null;
  dob: string | null;
  gender: string | null;
  weight: number | null;
  disease: string[];
  medication: string[];
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
  setUserFromMe: (me: MeResponse) => void;
  refreshProfile: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

const initialUserProfile: UserProfile = {
  id: null,
  email: null,
  name: null,
  avatarUrl: null,
  dob: null,
  gender: null,
  weight: null,
  disease: [],
  medication: [],
};

const mapMeToUser = (me: MeResponse): UserProfile => ({
  id: null,
  email: me.email,
  name: me.username,
  avatarUrl: null,
  dob: me.dob ?? null,
  gender: me.gender ?? null,
  weight: me.weight ?? null,
  disease: me.disease ?? [],
  medication: me.medication ?? [],
});

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
          accessToken: response.access_token,
          user: { ...initialUserProfile, name: response.username },
        });
        const me = await authService.getMe();
        set({
          user: mapMeToUser(me),
          isAuthenticated: true,
          hasCompletedOnboarding: me.dob != null,
        });
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

      setUserFromMe: (me) =>
        set({
          user: mapMeToUser(me),
          hasCompletedOnboarding: me.dob != null,
        }),

      refreshProfile: async () => {
        const me = await authService.getMe();
        set({
          user: mapMeToUser(me),
          hasCompletedOnboarding: me.dob != null,
        });
      },
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