import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { UserGoalsScreen } from '../../screens/onboarding/UserGoalsScreen';
import { SymptomFoodBankScreen } from '../../screens/onboarding/SymptomFoodBankScreen';
import { UserProfileScreen } from '../../screens/onboarding/UserProfileScreen';

export type OnboardingStackParamList = {
  UserProfile: undefined;
  UserGoals: undefined;
  SymptomFoodBank: undefined;
};

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export const OnboardingStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="UserProfile" component={UserProfileScreen} />
    <Stack.Screen name="UserGoals" component={UserGoalsScreen} />
    <Stack.Screen name="SymptomFoodBank" component={SymptomFoodBankScreen} />
  </Stack.Navigator>
);
