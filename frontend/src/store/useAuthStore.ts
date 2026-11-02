import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService, MeResponse } from '../api/auth_service';
import { clerkSignIn, clerkSignOut, clerkSignUp } from '../auth/clerkSession';
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

interface LoginPayload {
  username: string;
  password: string;
}

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

interface AuthState {
  isAuthenticated: boolean;
  hasCompletedOnboarding: boolean;
  user: UserProfile;
}

interface AuthActions {
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  setSignedIn: () => void;
  clearLocal: () => void;
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

const clearedSession = {
  isAuthenticated: false,
  hasCompletedOnboarding: false,
  user: initialUserProfile,
};

const initialState: AuthState = {
  isAuthenticated: false,
  hasCompletedOnboarding: false,
  user: initialUserProfile,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      login: async (payload) => {
        await clerkSignIn(payload.username, payload.password);
        const me = await authService.getMe();
        set({
          user: mapMeToUser(me),
          isAuthenticated: true,
          hasCompletedOnboarding: me.dob != null,
        });
      },

      register: async (payload) => {
        await clerkSignUp(payload.username, payload.email, payload.password);
        const me = await authService.getMe();
        set({
          user: mapMeToUser(me),
          isAuthenticated: true,
          hasCompletedOnboarding: me.dob != null,
        });
      },

      setSignedIn: () => set({ isAuthenticated: true }),

      clearLocal: () => {
        useBankStore.getState().clearBank();
        set(clearedSession);
      },

      logout: () => {
        useBankStore.getState().clearBank();
        set(clearedSession);
        void clerkSignOut().catch(() => {});
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
        hasCompletedOnboarding: state.hasCompletedOnboarding,
        user: state.user,
      }),
    }
  )
);
