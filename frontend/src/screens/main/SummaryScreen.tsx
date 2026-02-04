
import { View, Button, StyleSheet, Text } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';

export function SummaryScreen() {
  const navigation = useAppNavigation();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>YOUR SUMMARY</Text>
      <Button title='To...' onPress={() => {navigation.navigate("Summary")}} />
      <Text style={styles.text}> {GetPersonalizedIntro("Nicole", "stomache pain", "pizza", 5, 10)} </Text>
      <Button title="VIEW ALL CORRELATIONS →" onPress={() => {}} />
      <Button title="+ ADD DATA" onPress={() => {}} />
    </View>
  );
}

function GetPersonalizedIntro(name: string, symptom: string, food: string, numerator: number, denominator: number) {
  return `${name}, in the last 7 days, your ${symptom} has correlated with eating ${food} ${numerator}/${denominator} times.`
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
    textAlign: 'center',
    color: "#b2939b",
  },
  text: {
    textAlign: 'center',
    color: '#000000',
  },
  body: {
    backgroundColor: "linear-gradient(to bottom, #ffffff, #fca450)"
  },
});