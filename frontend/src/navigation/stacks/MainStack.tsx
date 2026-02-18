
import React from 'react';
import { View } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

export type MainStackParamList = {
  MainPlaceholder: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

const MainPlaceholder = () => <View />;

export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="MainPlaceholder" component={MainPlaceholder} />
  </Stack.Navigator>
);