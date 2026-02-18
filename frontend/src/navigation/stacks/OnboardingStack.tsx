import React from 'react';
import { View } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

export type OnboardingStackParamList = {
  OnboardingPlaceholder: undefined;
};

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

const OnboardingPlaceholder = () => <View />;

export const OnboardingStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="OnboardingPlaceholder" component={OnboardingPlaceholder} />
  </Stack.Navigator>
);