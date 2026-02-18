import React from 'react';
import { View, Button, Text } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../../store/useAuthStore';

export type MainStackParamList = {        
  MainPlaceholder: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

const MainPlaceholder = () => {
  const logout = useAuthStore((s) => s.logout);

  return (
    <View>
      <Text>Main Placeholder</Text>
      <Button title="Log Out" onPress={logout} />
    </View>
  );
};
 
export const MainStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
    <Stack.Screen name="MainPlaceholder" component={MainPlaceholder} />
  </Stack.Navigator>
);