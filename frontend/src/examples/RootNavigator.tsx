import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ChocolatesScreen } from './ChocolatesScreen';

export type RootStackParamList = {
  Chocolates: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Chocolates" component={ChocolatesScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}