import { RootNavigator } from './src/navigation/RootNavigator';
import { setOnUnauthenticated } from './src/api/client';
import { useAuthStore } from './src/store/useAuthStore';
import { useNetInfo } from '@react-native-community/netinfo';
import { NoConnectionScreen } from './src/screens/NoConnectionScreen';
import "./global.css";

// Register synchronously so any 401 — including the very first API call —
// triggers a logout before React has a chance to render a broken state.
setOnUnauthenticated(() => useAuthStore.getState().logout());

export default function App() {
  const netInfo = useNetInfo();

  if (netInfo.isConnected === false) {
    return <NoConnectionScreen />;
  }
  return <RootNavigator />;
}