import React from 'react';
import { View, Button, Text, SafeAreaView } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../../store/useAuthStore';

export type OnboardingStackParamList = {
  OnboardingPlaceholder: undefined;
};

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

const OnboardingPlaceholder = () => {
  const completeOnboarding = useAuthStore((s) => s.completeOnboarding);

  return (
    <SafeAreaView>
      <Text>Onboarding Placeholder</Text>
      <Button title="Complete Onboarding" onPress={completeOnboarding} />  
    </SafeAreaView>
  );
};
 
export const OnboardingStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="OnboardingPlaceholder" component={OnboardingPlaceholder} />
  </Stack.Navigator>
);
