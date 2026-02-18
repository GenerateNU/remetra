import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LandingScreen } from '../../screens/auth/LandingScreen';

export type AuthStackParamList = {
  Landing: undefined;
  // Signup: undefined; // will do later
  // Login: undefined; // will do later
};

const Stack = createNativeStackNavigator<AuthStackParamList>();

export const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Landing" component={LandingScreen} />
  </Stack.Navigator>
);