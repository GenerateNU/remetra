import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MainTabs } from '../MainTabs';
import { BarcodeScannerScreen } from '../../components/BarcodeScannerScreen';
import { CorrelationsScreen } from '../../screens/main/CorrelationsScreen';
import { AboutScreen } from '../../screens/main/AboutScreen';
import { EditWeightScreen } from '../../screens/main/EditWeightScreen';
import { EditConditionsScreen } from '../../screens/main/EditConditionsScreen';
import { EditMedicationsScreen } from '../../screens/main/EditMedicationsScreen';

export type MainStackParamList = {
  Tabs: undefined;
  BarcodeScanner: { onScanned?: (food: { name: string; ingredients: string[] }) => void };
  Correlations: { initialSymptomId?: string } | undefined;
  About: undefined;
  EditWeight: undefined;
  EditConditions: undefined;
  EditMedications: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="Tabs" component={MainTabs} />
    <Stack.Screen name="BarcodeScanner" component={BarcodeScannerScreen} />
    <Stack.Screen name="Correlations" component={CorrelationsScreen} />
    <Stack.Screen
      name="About"
      component={AboutScreen}
      options={{ headerShown: true, headerBackTitle: 'Back', title: 'About', gestureEnabled: true }}
    />
    <Stack.Screen
      name="EditWeight"
      component={EditWeightScreen}
      options={{ headerShown: true, headerBackTitle: 'Back', title: 'Edit Weight', gestureEnabled: true }}
    />
    <Stack.Screen
      name="EditConditions"
      component={EditConditionsScreen}
      options={{ headerShown: true, headerBackTitle: 'Back', title: 'Edit Conditions', gestureEnabled: true }}
    />
    <Stack.Screen
      name="EditMedications"
      component={EditMedicationsScreen}
      options={{ headerShown: true, headerBackTitle: 'Back', title: 'Edit Medications', gestureEnabled: true }}
    />
  </Stack.Navigator>
);
