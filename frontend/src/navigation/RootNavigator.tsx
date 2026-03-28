import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useAuthStore } from '../store/useAuthStore';
import { AuthStack } from './stacks/AuthStack';
import { OnboardingStack } from './stacks/OnboardingStack';
import { MainStack } from './stacks/MainStack';

export const RootNavigator = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hasCompletedOnboarding = useAuthStore((s) => s.hasCompletedOnboarding);

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