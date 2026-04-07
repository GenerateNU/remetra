import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
<<<<<<< HEAD
import { SummaryScreen } from '../../screens/main/SummaryScreen';
import { CorrelationsScreen } from '../../screens/main/CorrelationsScreen';

export type MainStackParamList = {
  Summary: undefined;
  Correlations: undefined;
=======
import { MainTabs } from '../MainTabs';
import { BarcodeScannerScreen } from '../../components/BarcodeScannerScreen';
import { SymptomDetailScreen } from '../../screens/main/SymptomDetailScreen';

export type MainStackParamList = {
  Tabs: undefined;
  BarcodeScanner: { onScanned?: (food: { name: string; ingredients: string[] }) => void };
  SymptomDetail: { symptomId: string; symptomName: string };
>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
};

const Stack = createNativeStackNavigator<MainStackParamList>();

export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
<<<<<<< HEAD
    <Stack.Screen name="Summary" component={SummaryScreen} />
    <Stack.Screen name="Correlations" component={CorrelationsScreen} />
=======
    <Stack.Screen name="Tabs" component={MainTabs} />
    <Stack.Screen name="BarcodeScanner" component={BarcodeScannerScreen} />
    <Stack.Screen name="SymptomDetail" component={SymptomDetailScreen} />
>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
  </Stack.Navigator>
);
