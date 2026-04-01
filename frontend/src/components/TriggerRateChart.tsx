import { VictoryBar, VictoryChart, VictoryTheme, VictoryAxis } from 'victory-native';
import { View, Text } from 'react-native';

export interface ChartAssociation {
  food_name: string;
  trigger_rate: number;
}

interface Props {
  data: ChartAssociation[];
  title?: string;
}

export function TriggerRateChart({ data, title = 'Top Food Correlations' }: Props) {
  const sorted = [...data].sort((a, b) => b.trigger_rate - a.trigger_rate).slice(0, 5);

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-2">{title}</Text>
      <VictoryChart
        theme={VictoryTheme.material}
        domainPadding={20}
        height={220}
      >
        <VictoryAxis
          tickFormat={sorted.map(d => d.food_name)}
          style={{ tickLabels: { fontSize: 10 } }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(t: number) => `${Math.round(t * 100)}%`}
        />
        <VictoryBar
          data={sorted}
          x="food_name"
          y="trigger_rate"
          style={{ data: { fill: '#ca5e5e' } }}
          cornerRadius={4}
        />
      </VictoryChart>
    </View>
  );
}
