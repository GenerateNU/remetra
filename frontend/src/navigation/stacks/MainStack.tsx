import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SummaryScreen } from '../../screens/main/SummaryScreen';
import { CorrelationsScreen } from '../../screens/main/CorrelationsScreen';

export type MainStackParamList = {
  Summary: undefined;
  Correlations: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Summary" component={SummaryScreen} />
    <Stack.Screen name="Correlations" component={CorrelationsScreen} />
  </Stack.Navigator>
);