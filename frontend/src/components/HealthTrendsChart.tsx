/**
 * SAMPLE 1 of 3 — Health Trends chart (live on AnalysisScreen).
 *
 * Design: one metric at a time (Sleep / HRV / Resting HR toggle) on a single line chart,
 * 7 / 30 / 90-day range toggle, symptom days as markers on the time axis, null days left as gaps.
 */
import { useMemo, useState } from 'react';
import { VictoryChart, VictoryLine, VictoryScatter, VictoryAxis, VictoryTheme } from 'victory-native';
import { View, Text, useWindowDimensions } from 'react-native';
import type { HealthDayResponse } from '../api/health_service';
import { SegmentedControl } from './SegmentedControl';
import {
  buildHealthChartData,
  hasAnyHealthData,
  HealthMetric,
  HealthRange,
} from '../utils/healthChartData';

// Calm hues, no red (validated for colorblind separation). Only one metric shows at a time,
// and its name is always in the legend, so identity never rests on color alone.
const METRICS: { key: HealthMetric; label: string; subtitle: string; color: string }[] = [
  { key: 'sleep', label: 'Sleep', subtitle: 'Hours asleep per night', color: '#2a78d6' },
  { key: 'hrv', label: 'HRV', subtitle: 'Heart rate variability (ms)', color: '#1baf7a' },
  { key: 'restingHr', label: 'Resting HR', subtitle: 'Resting heart rate (bpm)', color: '#6250d6' },
];

const RANGES: HealthRange[] = [7, 30, 90];
const TICK_STEP: Record<HealthRange, number> = { 7: 1, 30: 7, 90: 15 };
const DOT_SIZE: Record<HealthRange, number> = { 7: 3.5, 30: 2.5, 90: 1.8 };
const SYMPTOM_MARKER_COLOR = '#b2939b';
const CHART_HEIGHT = 220;

interface Props {
  days: HealthDayResponse[]; // /health/trends response covering at least the longest range
  end: string; // YYYY-MM-DD, last day shown
}

function formatTick(d: Date): string {
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export function HealthTrendsChart({ days, end }: Props) {
  const { width } = useWindowDimensions();
  // Screen has 24px padding each side, card has 16px (p-4) each side
  const chartWidth = width - 48 - 32;

  const [metric, setMetric] = useState<HealthMetric>('sleep');
  const [range, setRange] = useState<HealthRange>(30);

  const data = useMemo(() => buildHealthChartData(days, metric, range, end), [days, metric, range, end]);

  if (!hasAnyHealthData(days)) {
    return (
      <View className="bg-white/35 rounded-xl p-5 mt-4">
        <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
          No Apple Health data yet
        </Text>
        <Text className="text-remetra-muted text-center text-sm">
          Once your sleep, HRV, and resting heart rate sync from Apple Health, they&apos;ll show up here alongside the
          days you logged symptoms.
        </Text>
      </View>
    );
  }

  const meta = METRICS.find((m) => m.key === metric)!;
  const readings = data.points.filter((p) => p.y !== null);
  const step = TICK_STEP[range];
  const last = data.points.length - 1;
  // Count ticks back from the last day so the most recent date is always labeled
  const tickValues = data.points.filter((_, i) => (last - i) % step === 0).map((p) => p.x);
  const [yMin] = data.domain.y;

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Health Trends</Text>
      <Text className="text-center text-xs text-gray-500 mb-3">{meta.subtitle}</Text>

      <SegmentedControl
        options={METRICS.map((m) => ({ value: m.key, label: m.label }))}
        selected={metric}
        onSelect={setMetric}
      />
      <View className="h-2" />
      <SegmentedControl
        options={RANGES.map((r) => ({ value: r, label: `${r} days` }))}
        selected={range}
        onSelect={setRange}
      />

      {data.hasMetricData ? (
        <View
          accessible
          accessibilityLabel={`${meta.label} over the last ${range} days: ${readings.length} days with data, ${data.symptomDays.length} symptom days marked`}
        >
          <VictoryChart
            theme={VictoryTheme.material}
            width={chartWidth}
            height={CHART_HEIGHT}
            scale={{ x: 'time' }}
            domain={data.domain}
            domainPadding={{ x: 8 }}
            padding={{ left: 36, right: 16, top: 16, bottom: 36 }}
          >
            <VictoryAxis
              tickValues={tickValues}
              tickFormat={(t: Date) => formatTick(new Date(t))}
              style={{
                tickLabels: { fontSize: 9, fill: '#666' },
                axis: { stroke: '#ddd' },
                ticks: { stroke: 'transparent' },
                grid: { stroke: 'transparent' },
              }}
            />
            <VictoryAxis
              dependentAxis
              tickCount={4}
              style={{
                tickLabels: { fontSize: 9, fill: '#666' },
                axis: { stroke: '#ddd' },
                grid: { stroke: '#f0f0f0' },
              }}
            />
            {/* null y values break the line, so missing days stay gaps */}
            <VictoryLine data={data.points} style={{ data: { stroke: meta.color, strokeWidth: 2 } }} />
            {/* Dots keep isolated readings (with gaps on both sides) visible */}
            <VictoryScatter
              data={readings}
              size={DOT_SIZE[range]}
              style={{ data: { fill: meta.color, stroke: '#fff', strokeWidth: 1 } }}
            />
            {/* Symptom days sit on the time axis */}
            <VictoryScatter
              data={data.symptomDays.map((x) => ({ x, y: yMin }))}
              symbol="triangleUp"
              size={4}
              style={{ data: { fill: SYMPTOM_MARKER_COLOR } }}
            />
          </VictoryChart>
        </View>
      ) : (
        <View style={{ height: CHART_HEIGHT, justifyContent: 'center' }}>
          <Text className="text-remetra-muted text-center text-sm">
            No {meta.label} data in the last {range} days.
          </Text>
        </View>
      )}

      {/* Legend */}
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 16, marginTop: 4 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 12, height: 2, borderRadius: 1, backgroundColor: meta.color }} />
          <Text style={{ fontSize: 11, color: '#666' }}>{meta.label}</Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <Text style={{ fontSize: 9, color: SYMPTOM_MARKER_COLOR }}>▲</Text>
          <Text style={{ fontSize: 11, color: '#666' }}>Symptom logged</Text>
        </View>
      </View>
    </View>
  );
}
