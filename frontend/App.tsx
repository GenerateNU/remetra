import { ClerkProvider } from '@clerk/expo';
import { tokenCache } from '@clerk/expo/token-cache';
import { useNetInfo } from '@react-native-community/netinfo';
import { RootNavigator } from './src/navigation/RootNavigator';
import { ClerkSessionBridge } from './src/auth/ClerkSessionBridge';
import { NoConnectionScreen } from './src/screens/NoConnectionScreen';
import "./global.css";

const publishableKey = process.env.EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY!;

export default function App() {
  const netInfo = useNetInfo();

  return (
    <ClerkProvider publishableKey={publishableKey} tokenCache={tokenCache}>
      <ClerkSessionBridge />
      {netInfo.isConnected === false ? <NoConnectionScreen /> : <RootNavigator />}
    </ClerkProvider>
  );
}
