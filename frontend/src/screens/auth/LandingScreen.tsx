
import { View, Text, StyleSheet } from 'react-native';

// When adding navigation, uncomment:
// import type { NativeStackScreenProps } from '@react-navigation/native-stack';
// import type { YourStackParamList } from '../../navigation/YourStack';
// type Props = NativeStackScreenProps<YourStackParamList, 'ScreenName'>;

export function LandingScreen() {
  // When adding navigation, change to: export function ScreenName({ navigation }: Props)

  return (
    <View style={styles.container}>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
  },
});