import { VictoryChart, VictoryBar, VictoryStack, VictoryAxis, VictoryTheme } from 'victory-native';
import { View, Text, useWindowDimensions } from 'react-native';

const SYMPTOM_COLORS = ['#ca5e5e', '#b2939b', '#fd9055', '#B8624F', '#8B7E74', '#6B8E6B', '#7B9EC4'];

interface SymptomLog {
  symptom_id: string;
  timestamp: string;
}

interface Props {
  logs: SymptomLog[];
  symptomNames: Record<string, string>;
}

function getWeekStart(date: Date): string {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  d.setDate(diff);
  d.setHours(0, 0, 0, 0);
  return d.toISOString().slice(0, 10);
}

function formatWeekLabel(isoDate: string): string {
  const d = new Date(isoDate + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatShortLabel(isoDate: string): string {
  const d = new Date(isoDate + 'T00:00:00');
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatName(name: string): string {
  return name
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function SymptomsOverTimeChart({ logs, symptomNames }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = width - 32;

  if (logs.length === 0) return null;

  // Bucket logs by week and symptom
  const countsByWeek: Record<string, Record<string, number>> = {};
  for (const log of logs) {
    const week = getWeekStart(new Date(log.timestamp));
    if (!countsByWeek[week]) countsByWeek[week] = {};
    countsByWeek[week][log.symptom_id] = (countsByWeek[week][log.symptom_id] ?? 0) + 1;
  }

  const weeks = Object.keys(countsByWeek).sort();
  if (weeks.length < 2) return null;

  // Collect unique symptom IDs in order of total frequency
  const symptomTotals: Record<string, number> = {};
  for (const weekCounts of Object.values(countsByWeek)) {
    for (const [sid, count] of Object.entries(weekCounts)) {
      symptomTotals[sid] = (symptomTotals[sid] ?? 0) + count;
    }
  }
  const symptomIds = Object.entries(symptomTotals)
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => id);

  // Adaptive label sizing based on week count
  const weekCount = weeks.length;
  const useShortLabels = weekCount > 8;
  const labelFormatter = useShortLabels ? formatShortLabel : formatWeekLabel;
  const weekLabels = weeks.map(labelFormatter);
  const tickFontSize = weekCount > 16 ? 7 : weekCount > 8 ? 8 : 9;
  const tickAngle = weekCount > 6 ? -45 : 0;
  const bottomPadding = tickAngle !== 0 ? 55 : 40;

  // Show fewer ticks when there are many weeks
  const maxVisibleTicks = Math.floor((chartWidth - 70) / 40);
  const tickInterval = weekCount > maxVisibleTicks ? Math.ceil(weekCount / maxVisibleTicks) : 1;
  const tickValues = weekLabels.filter((_, i) => i % tickInterval === 0);

  // Build per-symptom data arrays (one entry per week, y=0 if absent)
  const seriesData = symptomIds.map(sid =>
    weeks.map((week, i) => ({
      x: weekLabels[i],
      y: countsByWeek[week][sid] ?? 0,
    })),
  );

  const legendData = symptomIds.map((sid, i) => ({
    name: formatName(symptomNames[sid] ?? sid),
    fill: SYMPTOM_COLORS[i % SYMPTOM_COLORS.length],
  }));

  const chartHeight = 260;

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Symptoms Over Time</Text>
      <Text className="text-center text-xs text-gray-500 mb-2">
        Weekly breakdown by symptom
      </Text>
      <VictoryChart
        theme={VictoryTheme.material}
        width={chartWidth}
        height={chartHeight}
        domainPadding={{ x: 15 }}
        padding={{ left: 25, right: 30, top: 10, bottom: bottomPadding }}
      >
        <VictoryAxis
          tickValues={tickValues}
          style={{
            tickLabels: {
              fontSize: tickFontSize,
              angle: tickAngle,
              textAnchor: tickAngle !== 0 ? 'end' : 'middle',
              fill: '#666',
            },
            axis: { stroke: '#ddd' },
            grid: { stroke: 'transparent' },
          }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(t: number) => (Number.isInteger(t) ? String(t) : '')}
          style={{
            tickLabels: { fontSize: 9, fill: '#666' },
            axis: { stroke: '#ddd' },
            grid: { stroke: '#f0f0f0' },
          }}
        />
        <VictoryStack>
          {seriesData.map((data, i) => (
            <VictoryBar
              key={symptomIds[i]}
              data={data}
              style={{ data: { fill: SYMPTOM_COLORS[i % SYMPTOM_COLORS.length] } }}
              cornerRadius={{ topLeft: i === seriesData.length - 1 ? 2 : 0, topRight: i === seriesData.length - 1 ? 2 : 0 }}
            />
          ))}
        </VictoryStack>
      </VictoryChart>
      {/* Legend */}
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 12, marginTop: 4 }}>
        {legendData.map(item => (
          <View key={item.name} style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
            <View style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: item.fill }} />
            <Text style={{ fontSize: 11, color: '#666' }}>{item.name}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}
