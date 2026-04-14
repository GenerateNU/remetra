import { VictoryChart, VictoryScatter, VictoryAxis, VictoryTheme, VictoryLabel } from 'victory-native';
import { View, Text, useWindowDimensions } from 'react-native';
import { Association } from './AssociationCard';

interface Props {
  data: Association[];
}

export function FishersExposuresChart({ data }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = width - 32;

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Statistical Significance</Text>
      <Text className="text-center text-xs text-gray-500 mb-2">
        Top-right = frequent &amp; significant — strongest triggers
      </Text>
      <VictoryChart
        theme={VictoryTheme.material}
        width={chartWidth}
        height={240}
        padding={{ left: 55, right: 60, top: 30, bottom: 50 }}
      >
        <VictoryAxis
          label="Exposures"
          style={{
            axisLabel: { fontSize: 10, padding: 30 },
            tickLabels: { fontSize: 9 },
          }}
        />
        <VictoryAxis
          dependentAxis
          label="p-value (lower = significant)"
          domain={[0, 1]}
          style={{
            axisLabel: { fontSize: 9, padding: 40 },
            tickLabels: { fontSize: 9 },
          }}
        />
        <VictoryScatter
          data={data}
          x="exposures"
          y="fishers_p_value"
          labels={({ datum }: { datum: Association }) => datum.food_name}
          labelComponent={<VictoryLabel style={{ fontSize: 8 }} dy={-10} />}
          style={{ data: { fill: '#b2939b', opacity: 0.85 } }}
          size={7}
        />
      </VictoryChart>
    </View>
  );
}
