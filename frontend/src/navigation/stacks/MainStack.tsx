import React from 'react';
import { View, Button, Text } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../../store/useAuthStore';
import { SummaryScreen } from '../../screens/main/SummaryScreen';

export type MainStackParamList = {        
  Summary: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

 
export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Summary" component={SummaryScreen} />
  </Stack.Navigator>
);