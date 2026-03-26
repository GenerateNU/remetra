import { useEffect } from 'react';
import { RootNavigator } from './src/navigation/RootNavigator';
import { setOnUnauthenticated } from './src/api/client';
import { useAuthStore } from './src/store/useAuthStore';
import "./global.css";

export default function App() {
  useEffect(() => {
    setOnUnauthenticated(() => useAuthStore.getState().logout());
  }, []);
  return <RootNavigator />;
}