import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MainTabs } from '../MainTabs';
import { BarcodeScannerScreen } from '../../components/BarcodeScannerScreen';

export type MainStackParamList = {
  Tabs: undefined;
  BarcodeScanner: { onScanned?: (food: { name: string; ingredients: string[] }) => void };
};

const Stack = createNativeStackNavigator<MainStackParamList>();

export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Tabs" component={MainTabs} />
    <Stack.Screen name="BarcodeScanner" component={BarcodeScannerScreen} />
  </Stack.Navigator>
);
