import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { AuthStackParamList } from './stacks/AuthStack';

export const useAppNavigation = () =>
  useNavigation<NativeStackNavigationProp<AuthStackParamList>>();