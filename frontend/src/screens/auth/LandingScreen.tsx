
import { View, StyleSheet, Button } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';

export function LandingScreen() {
  const navigation = useAppNavigation();

  return (
    <View style={styles.container}>
      <Button title='To Onboarding 1' onPress={() => {navigation.navigate("UserGoals");}} />
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