
import { View, Button, StyleSheet, Text } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useAppNavigation } from '../../navigation/hooks';
import {VictoryBar, VictoryChart, VictoryTheme, VictoryAxis } from 'victory-native';

function GenericCorrelationChart() {
  const data = [
    { food: 'Pizza', correlation: 0.7 },
    { food: 'Dairy', correlation: 0.4 },
    { food: 'Spicy', correlation: 0.6 },
    { food: 'Sugar', correlation: 0.2 },
  ];

  return (
    <View style={styles.chartContainer}>
      <Text style={styles.chartTitle}>Top Food Correlations</Text>

      <VictoryChart
        theme={VictoryTheme.material}
        domainPadding={20}
        height={220}
      >
        <VictoryAxis
          tickFormat={data.map(d => d.food)}
          style={{
            tickLabels: { fontSize: 10 },
          }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(t: number) => `${Math.round(t * 100)}%`}

        />

        <VictoryBar
          data={data}
          x="food"
          y="correlation"
          style={{
            data: { fill: '#ca5e5e' },
          }}
          cornerRadius={4}
        />
      </VictoryChart>
    </View>
  );
}

export function SummaryScreen() {
  const navigation = useAppNavigation();

  return (
    <View className="flex-1 relative">
      <BackgroundGradient />
        <Text style={styles.title}>YOUR SUMMARY</Text>
        <Text style={styles.text}> {GetPersonalizedIntro("Nicole", "stomache pain", "pizza", 5, 10)} </Text>
        <GenericCorrelationChart />

        <View style={styles.button}>
          <Button color={"#ca5e5e"} title="VIEW ALL CORRELATIONS -->" onPress={() => {}} />
        </View>
        <View style={styles.button}>
          <Button color={"#ca5e5e"} title="+ Add Data" onPress={() => {}} />
        </View>
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
    fontSize: 16,
  },
  button: {
    margin: "10%",

  },
  
  chartContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginVertical: 16,
  },
  
  chartTitle: {
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  
});