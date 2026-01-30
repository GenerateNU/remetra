
import { View, Button, StyleSheet } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';

export function UserGoalsScreen() {
  const navigation = useAppNavigation();

  return (
    <View style={styles.container}>
      <Button title='To Onboarding 2' onPress={() => {navigation.navigate("SymptomFoodBank");}} />
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