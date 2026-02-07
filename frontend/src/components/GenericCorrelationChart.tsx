import {VictoryBar, VictoryChart, VictoryTheme, VictoryAxis } from 'victory-native';
import { View, Text } from 'react-native';

export function GenericCorrelationChart() {
  const data = [
    { food: 'Pizza', correlation: 0.7 },
    { food: 'Dairy', correlation: 0.4 },
    { food: 'Spicy', correlation: 0.6 },
    { food: 'Sugar', correlation: 0.2 },
  ];

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-2">
        Top Food Correlations
      </Text>

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