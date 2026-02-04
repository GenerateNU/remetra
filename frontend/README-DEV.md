# Frontend

React Native (Expo) frontend for Remetra.

## Quick Start

```bash
cd frontend
npm install
npx expo start
```

## Stack

| Purpose | Library |
|---------|---------|
| Navigation | [React Navigation](https://reactnavigation.org/) |
| Safe Areas (Top Bar) | [expo-safe-area-context](https://docs.expo.dev/versions/latest/sdk/safe-area-context/) |
| State | [Zustand](https://zustand.docs.pmnd.rs/getting-started/introduction) |
| HTTP | [Axios](https://axios-http.com/) |
| Linting | ESLint |

## Project Structure

```
src/
├── api/           # Axios client + endpoint functions
├── components/    # Reusable UI components
├── hooks/         # Custom hooks (ViewModels)
├── navigation/    # Navigator configs
├── screens/       # Screen components
├── store/         # Zustand stores
└── types/         # TypeScript types
```

## Patterns

### State Management (Zustand)

Zustand stores live in `src/store/`. A Zustand store can be used to manage a specified set of values, or, a state. For example, if you need to manage a signed-in users authentication token, the following would be a good way to do so.

```typescript
// src/store/useAuthStore.ts
import { create } from 'zustand';

interface AuthState {
  token: string | null;
  setToken: (token: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  setToken: (token) => set({ token }),
  logout: () => set({ token: null }),
}));
```

Zustand allows for global access to all stores. This is how you would use the useAuthStore in a component:

```typescript
// Zustand selector pattern to avoid unnecessary re-renders
const token = useAuthStore((state) => state.token);
const logout = useAuthStore((state) => state.logout);
```

You should NOT be calling Zustand stores like this:
```typescript
const { token, logout } = useAuthStore();
```

This would trigger the component to re-render upon any update to the store (any value in the store being updated, even if we aren't accessing it in the component)

### API Layer

All API calls go through the configured Axios client.

```typescript
// src/api/client.ts — configured with baseURL, interceptors, etc.
// src/api/endpoints.ts — all endpoint functions

// Adding a new endpoint:
export const api = {
  getUsers: async (): Promise<User[]> => {
    const { data } = await apiClient.get<User[]>('/users');
    return data;
  },
};
```

### Custom Hooks (ViewModel Pattern)

Encapsulate data fetching + state logic in hooks. These are then called by screens to present the data (as seen below)

```typescript
// src/hooks/useUsers.ts
export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getUsers();
      setUsers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { users, isLoading, error, fetch };
}
```

### Screens

Screens are thin. They wire up hooks and render UI.

```typescript
// src/screens/UsersScreen.tsx
export function UsersScreen() {
  const { users, isLoading, fetch } = useUsers();

  useEffect(() => { fetch(); }, [fetch]);

  if (isLoading) return <LoadingSpinner />;

  return (
    <SafeAreaView style={styles.container}>
      {users.map((user) => <UserCard key={user.id} user={user} />)}
    </SafeAreaView>
  );
}
```

### Safe Areas

Always wrap screen content in `SafeAreaView` or use the hook:

```typescript
import { SafeAreaView } from 'react-native-safe-area-context';

// Option 1: Wrap content
<SafeAreaView style={{ flex: 1 }}>
  {/* screen content */}
</SafeAreaView>

// Option 2: Use the hook for granular control
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const insets = useSafeAreaInsets();
<View style={{ paddingTop: insets.top }}>{/* ... */}</View>
```

## Adding a New Feature

1. **Types** — Add interfaces to `src/types/`
2. **API** — Add endpoint function to `src/api/endpoints.ts`
3. **Hook** — Create `src/hooks/useFeature.ts` with fetch logic
4. **Screen** — Create `src/screens/FeatureScreen.tsx`
5. **Navigation** — Register screen in the appropriate navigator
6. **Test** — Add tests to `src/hooks/__tests__/`

## Commands

```bash
# Development
npx expo start          # Start dev server
npx expo start --clear  # Clear cache and start

# Testing
npm test                # Run tests
npm test -- --watch     # Watch mode

# Linting
npm run lint            # Run ESLint
npm run lint -- --fix   # Auto-fix issues

# Type checking
npx tsc --noEmit        # Check types without emitting
```

## Environment Variables

Create `.env` in the frontend root:

```
EXPO_PUBLIC_API_URL=http://localhost:8000
```

Access in code:

```typescript
const baseUrl = process.env.EXPO_PUBLIC_API_URL;
```

## Conventions

- **File naming**: PascalCase for components/screens, camelCase for hooks/utils
- **Exports**: Named exports for everything except `App.tsx`
- **Styles**: `StyleSheet.create()` at bottom of component files
- **Types**: Colocate with usage, or in `src/types/` if shared