import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { AuthStackParamList } from './stacks/AuthStack';
import type { OnboardingStackParamList } from './stacks/OnboardingStack';
import type { MainStackParamList } from './stacks/MainStack';

export type AppParamList = AuthStackParamList & OnboardingStackParamList & MainStackParamList;

export const useAppNavigation = () =>
  useNavigation<NativeStackNavigationProp<AppParamList>>();