
import { View, Button, StyleSheet } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';

export function SummaryScreen() {
  const navigation = useAppNavigation();

  return (
    <View style={styles.container}>
      <Button title='To...' onPress={() => {navigation.navigate("Summary")}} />
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