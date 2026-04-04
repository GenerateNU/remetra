import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SummaryScreen } from '../../screens/main/SummaryScreen';
import { BarcodeScannerScreen } from '../../components/BarcodeScannerScreen';

export type MainStackParamList = {        
  Summary: undefined;
  BarcodeScanner: { onScanned?: (food: { name: string; ingredients: string[] }) => void };

};

const Stack = createNativeStackNavigator<MainStackParamList>();

 
export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Summary" component={SummaryScreen} />
    <Stack.Screen name="BarcodeScanner" component = {BarcodeScannerScreen} />
  </Stack.Navigator>
);