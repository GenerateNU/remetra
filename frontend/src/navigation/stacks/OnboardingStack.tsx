import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ConditionsScreen } from '../../screens/onboarding/ConditionsScreen';
import { ExclusionsScreen } from '../../screens/onboarding/ExclusionsScreen';
import { SuspicionsScreen } from '../../screens/onboarding/SuspicionsScreen';
import { RegularsScreen } from '../../screens/onboarding/RegularsScreen';

export type OnboardingStackParamList = {
  Conditions: undefined;
  Exclusions: undefined;
  Suspicions: undefined;
  Regulars: undefined;
};

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export const OnboardingStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Conditions" component={ConditionsScreen} />
    <Stack.Screen name="Exclusions" component={ExclusionsScreen} />
    <Stack.Screen name="Suspicions" component={SuspicionsScreen} />
    <Stack.Screen name="Regulars" component={RegularsScreen} />
  </Stack.Navigator>
);
