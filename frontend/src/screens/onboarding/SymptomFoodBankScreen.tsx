
import { View, Button, StyleSheet } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';
import { BackgroundGradient } from '../../components/BackgroundGradient';

export function SymptomFoodBankScreen() {
  const navigation = useAppNavigation();

  return (
    <View style={styles.container}>
      <BackgroundGradient />
      <Button title='To Summary (Main)' onPress={() => {navigation.navigate("Summary");}} />
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