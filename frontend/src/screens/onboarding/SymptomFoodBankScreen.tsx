
import { View, Button, StyleSheet } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useAuthStore } from '../../store/useAuthStore';


export function SymptomFoodBankScreen() {
  const completeOnboarding = useAuthStore((s) => s.completeOnboarding);


  return (
    <View style={styles.container}>
      <BackgroundGradient />
      <Button title='To Summary (Main)' onPress={completeOnboarding} />
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