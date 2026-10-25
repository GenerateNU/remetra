/**
 * SAMPLE 2 of 3 — Health breakdown donuts (live on AnalysisScreen, below Sample 1).
 *
 * Design: one donut per metric (Sleep / HRV / Resting HR toggle, same controls as Sample 1),
 * showing how the days in a 7 / 30 / 90-day range split across value bands. Bands are ordered,
 * so each metric uses one-hue ramp of its Sample 1 color (light = lower, dark = higher) and
 * nothing is red. "No data" is a neutral slice so the donut always equals the whole range.
 * A pie can't show change over time or mark symptom days, so this sample doesn't cover those
 * ticket items; Sample 1 does.
 */
import { useMemo, useState } from 'react';
import { VictoryPie } from 'victory-native';
import { View, Text } from 'react-native';
import type { HealthDayResponse } from '../api/health_service';
import { SegmentedControl } from './SegmentedControl';
import {
  buildMetricBreakdown,
  hasAnyHealthData,
  BreakdownBandKey,
  HealthMetric,
  HealthRange,
} from '../utils/healthChartData';

// Validated ordinal ramps (one hue, light -> dark; lightest step still clears 2:1 on white)
const NO_DATA_COLOR = '#e4e2dc';
const METRICS: {
  key: HealthMetric;
  label: string;
  subtitle: string;
  dayWord: string;
  ramp: [string, string, string, string];
}[] = [
  { key: 'sleep', label: 'Sleep', subtitle: 'How long you slept each night', dayWord: 'nights', ramp: ['#86b6ef', '#3987e5', '#1c5cab', '#0d366b'] },
  { key: 'hrv', label: 'HRV', subtitle: 'Your daily heart rate variability', dayWord: 'days', ramp: ['#5cc79f', '#1f9e70', '#13734f', '#0b4a33'] },
  { key: 'restingHr', label: 'Resting HR', subtitle: 'Your daily resting heart rate', dayWord: 'days', ramp: ['#a79ef0', '#7a6de2', '#5443c4', '#33278a'] },
];

const RANGES: HealthRange[] = [7, 30, 90];
const DONUT_SIZE = 160;

interface Props {
  days: HealthDayResponse[]; // /health/trends response covering at least the longest range
  end: string; // YYYY-MM-DD, last day included
}

function bandColor(key: BreakdownBandKey, ramp: string[]): string {
  return key === 'noData' ? NO_DATA_COLOR : ramp[Number(key.slice(4))];
}

export function HealthBreakdownPieChart({ days, end }: Props) {
  const [metric, setMetric] = useState<HealthMetric>('sleep');
  const [range, setRange] = useState<HealthRange>(30);
  const breakdown = useMemo(() => buildMetricBreakdown(days, metric, range, end), [days, metric, range, end]);

  if (!hasAnyHealthData(days)) {
    return (
      <View className="bg-white/35 rounded-xl p-5 mt-4">
        <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
          No Apple Health data yet
        </Text>
        <Text className="text-remetra-muted text-center text-sm">
          Once your sleep, HRV, and resting heart rate sync from Apple Health, you&apos;ll see how your days add up
          here.
        </Text>
      </View>
    );
  }

  const meta = METRICS.find((m) => m.key === metric)!;
  // Zero-count slices are left out of the pie but stay in the legend
  const slices = breakdown.bands
    .filter((b) => b.count > 0)
    .map((b) => ({ x: b.label, y: b.count, fill: bandColor(b.key, meta.ramp) }));

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Health Breakdown</Text>
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

      {breakdown.daysTracked === 0 ? (
        <View style={{ height: DONUT_SIZE, justifyContent: 'center' }} className="mt-3">
          <Text className="text-remetra-muted text-center text-sm">
            No {meta.label} data in the last {range} days.
          </Text>
        </View>
      ) : (
        <View
          className="flex-row items-center mt-3"
          accessible
          accessibilityLabel={`${meta.label} over the last ${range} ${meta.dayWord}: ${breakdown.bands
            .map((b) => `${b.label} ${b.count}`)
            .join(', ')}`}
        >
          <View style={{ width: DONUT_SIZE, height: DONUT_SIZE }}>
            <VictoryPie
              standalone
              width={DONUT_SIZE}
              height={DONUT_SIZE}
              padding={0}
              data={slices}
              innerRadius={DONUT_SIZE * 0.3}
              padAngle={1.5}
              labels={() => null}
              colorScale={slices.map((s) => s.fill)}
            />
            {/* Center label */}
            <View
              pointerEvents="none"
              style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' }}
            >
              <Text className="text-2xl font-semibold text-remetra-espresso">{breakdown.daysTracked}</Text>
              <Text style={{ fontSize: 10, color: '#666' }}>
                of {breakdown.totalDays} {meta.dayWord}
              </Text>
            </View>
          </View>

          {/* Legend with counts */}
          <View className="flex-1 ml-4 gap-2">
            {breakdown.bands.map((b) => (
              <View key={b.key} className="flex-row items-center">
                <View
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 2,
                    backgroundColor: bandColor(b.key, meta.ramp),
                    marginRight: 6,
                  }}
                />
                <Text style={{ fontSize: 12, color: '#666', flex: 1 }}>{b.label}</Text>
                <Text style={{ fontSize: 12, color: '#333', fontWeight: '600' }}>{b.count}</Text>
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );
}
