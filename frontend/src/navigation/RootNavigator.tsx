import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LandingScreen } from '../screens/auth/LandingScreen';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { SignupScreen } from '../screens/auth/SignupScreen';
import { SummaryScreen } from '../screens/main/SummaryScreen';
import { UserGoalsScreen } from '../screens/onboarding/UserGoalsScreen';
import { SymptomFoodBankScreen } from '../screens/onboarding/SymptomFoodBankScreen';

// This file will change a lot - eventually we will have a main stack + stacks for separate nav flows in the app
// Ex. auth, onboarding, and main will all have differnt nav stacks, centralized under mainStack

export type RootStackParamList = {
  Landing: undefined;
  Login: undefined;
  Signup: undefined;
  UserGoals: undefined
  SymptomFoodBank: undefined
  Summary: undefined
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Landing">
        <Stack.Screen name="Landing" component={LandingScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Signup" component={SignupScreen} />
        <Stack.Screen name="UserGoals" component={UserGoalsScreen} />
        <Stack.Screen name="SymptomFoodBank" component={SymptomFoodBankScreen} />
        <Stack.Screen name="Summary" component={SummaryScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}