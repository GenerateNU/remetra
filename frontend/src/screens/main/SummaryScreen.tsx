
import { View, Button, StyleSheet, Text } from 'react-native';
import {LinearGradient} from 'expo-linear-gradient';
import { useAppNavigation } from '../../navigation/hooks';

export function SummaryScreen() {
  const navigation = useAppNavigation();

  return (
    <LinearGradient style={styles.container} start={[0.5, 0.3]} end={[0.5, 1]} colors={["#ffffff", "#fca450"]}>
        <Text style={styles.title}>YOUR SUMMARY</Text>
        <Text style={styles.text}> {GetPersonalizedIntro("Nicole", "stomache pain", "pizza", 5, 10)} </Text>
        <View style={styles.button}>
          <Button color={"#ca5e5e"} title="VIEW ALL CORRELATIONS -->" onPress={() => {}} />
        </View>
        <View style={styles.button}>
          <Button color={"#ca5e5e"} title="+ Add Data →" onPress={() => {}} />
        </View>
    </LinearGradient>
  );
}

function GetPersonalizedIntro(name: string, symptom: string, food: string, numerator: number, denominator: number) {
  return `${name}, in the last 7 days, your ${symptom} has correlated with eating ${food} ${numerator}/${denominator} times.`
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    textAlign: 'center',
    color: "#b2939b",
    fontStyle: "italic",
  },
  text: {
    textAlign: 'center',
    color: '#000000',
    marginVertical: "10%",
    marginBottom: "90%",
    fontSize: 16,
  },
  button: {
    margin: "10%",
  }
});