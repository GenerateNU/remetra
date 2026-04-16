import { VictoryChart, VictoryBar, VictoryAxis, VictoryTheme, VictoryLabel } from 'victory-native';
import { View, Text, useWindowDimensions } from 'react-native';
import { Association } from './AssociationCard';

interface Props {
  data: Association[];
  title?: string;
}

function confidenceColor(p: number): string {
  if (p < 0.05) return '#4CAF50';
  if (p < 0.1) return '#FF9800';
  return '#9E9E9E';
}

export function ExcessRiskChart({ data, title }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = width - 32;

  // Compute excess risk, keep only positive values, sort ascending (highest at top)
  const processed = data
    .map(a => ({
      ingredient_name: a.ingredient_name,
      excess_risk: a.trigger_rate - a.base_rate,
      fishers_p_value: a.fishers_p_value,
    }))
    .filter(a => a.excess_risk > 0)
    .sort((a, b) => a.excess_risk - b.excess_risk);

  if (processed.length === 0) return null;

  // Truncate long ingredient names for axis labels
  const maxLabelLen = 14;
  const displayData = processed.map(d => ({
    ...d,
    label: d.ingredient_name.length > maxLabelLen
      ? d.ingredient_name.slice(0, maxLabelLen - 1) + '\u2026'
      : d.ingredient_name,
  }));

  const chartHeight = Math.max(200, displayData.length * 36 + 80);

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">
        {title ?? 'Risk Increase by Ingredient'}
      </Text>
      <Text className="text-center text-xs text-gray-500 mb-2">
        How much more likely a symptom is after eating each ingredient
      </Text>
      <VictoryChart
        horizontal
        theme={VictoryTheme.material}
        width={chartWidth}
        height={chartHeight}
        domainPadding={{ x: 15 }}
        padding={{ left: 110, right: 70, top: 20, bottom: 40 }}
      >
        <VictoryAxis
          style={{
            tickLabels: { fontSize: 10, fill: '#444' },
            axis: { stroke: 'transparent' },
            grid: { stroke: 'transparent' },
          }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(t: number) => `+${Math.round(t * 100)}%`}
          style={{
            axisLabel: { fontSize: 10, padding: 30 },
            tickLabels: { fontSize: 9 },
          }}
        />
        <VictoryBar
          data={displayData}
          x="label"
          y="excess_risk"
          cornerRadius={{ topLeft: 3, topRight: 3 }}
          labels={({ datum }) => `+${Math.round(datum.excess_risk * 100)}%`}
          labelComponent={<VictoryLabel dx={5} style={{ fontSize: 9, fill: '#555' }} />}
          style={{
            data: {
              fill: ({ datum }: any) => confidenceColor(datum.fishers_p_value),
            },
          }}
          barWidth={18}
        />
      </VictoryChart>
      {/* Confidence legend */}
      <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 12, marginTop: 4 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#4CAF50' }} />
          <Text style={{ fontSize: 10, color: '#888' }}>High confidence</Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#FF9800' }} />
          <Text style={{ fontSize: 10, color: '#888' }}>Medium</Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#9E9E9E' }} />
          <Text style={{ fontSize: 10, color: '#888' }}>Low</Text>
        </View>
      </View>
    </View>
  );
}
