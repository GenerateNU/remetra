import React, { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { useAuthStore } from '../store/useAuthStore';
import { AuthStack } from './stacks/AuthStack';
import { OnboardingStack } from './stacks/OnboardingStack';
import { MainStack } from './stacks/MainStack';

export const RootNavigator = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hasCompletedOnboarding = useAuthStore((s) => s.hasCompletedOnboarding);
  const [hydrated, setHydrated] = useState(() => useAuthStore.persist.hasHydrated());

  useEffect(() => {
    if (hydrated) return;
    return useAuthStore.persist.onFinishHydration(() => setHydrated(true));
  }, []);

  if (!hydrated) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator color="#b2939b" />
      </View>
    );
  }

  const renderStack = () => {
    if (!isAuthenticated) return <AuthStack />;
    if (!hasCompletedOnboarding) return <OnboardingStack />;
    return <MainStack />;
  };

  return (
    <NavigationContainer>
      {renderStack()}
    </NavigationContainer>
  );
};