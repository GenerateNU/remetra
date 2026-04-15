import { VictoryChart, VictoryScatter, VictoryAxis, VictoryTheme, VictoryLabel } from 'victory-native';
import { View, Text, useWindowDimensions } from 'react-native';

export interface ScatterPoint {
  ingredient_name: string;
  exposures: number;
  average_intensity: number;
}

interface Props {
  data: ScatterPoint[];
}

export function FrequencyIntensityChart({ data }: Props) {
  const { width } = useWindowDimensions();
  // 32px horizontal padding on the card (p-4 = 16 each side)
  const chartWidth = width - 32;

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Frequency vs. Severity</Text>
      <Text className="text-center text-xs text-gray-500 mb-2">
        Top-right = frequent &amp; intense — avoid these first
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
          label="Avg Intensity (1–10)"
          domain={[0, 10]}
          style={{
            axisLabel: { fontSize: 10, padding: 35 },
            tickLabels: { fontSize: 9 },
          }}
        />
        <VictoryScatter
          data={data}
          x="exposures"
          y="average_intensity"
          labels={({ datum }: { datum: ScatterPoint }) => datum.ingredient_name}
          labelComponent={<VictoryLabel style={{ fontSize: 8 }} dy={-10} />}
          style={{ data: { fill: '#ca5e5e', opacity: 0.85 } }}
          size={7}
        />
      </VictoryChart>
    </View>
  );
}
