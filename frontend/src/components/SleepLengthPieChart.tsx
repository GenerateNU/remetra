/**
 * SAMPLE 2 of 3 — Sleep length donut (live on AnalysisScreen, below Sample 1).
 *
 * Design: part-to-whole of the nights in a 7 / 30 / 90-day range, grouped by how long the user slept.
 * Bands are ordered, so they use one blue ramp (light = shorter, dark = longer) rather than
 * category colors, and nothing is red. "No data" is a neutral slice so the donut always equals
 * the whole range. A pie can't show change over time or mark symptom days, so this sample
 * doesn't cover those ticket items; Sample 1 does.
 */
import { useMemo, useState } from 'react';
import { VictoryPie } from 'victory-native';
import { View, Text } from 'react-native';
import type { HealthDayResponse } from '../api/health_service';
import { SegmentedControl } from './SegmentedControl';
import {
  buildSleepBreakdown,
  hasAnyHealthData,
  HealthRange,
  SleepBucketKey,
} from '../utils/healthChartData';

// Sequential blue ramp (one hue, light -> dark) + a neutral for missing nights
const BUCKET_COLORS: Record<SleepBucketKey, string> = {
  under6: '#86b6ef',
  '6to7': '#3987e5',
  '7to8': '#1c5cab',
  over8: '#0d366b',
  noData: '#e4e2dc',
};

const RANGES: HealthRange[] = [7, 30, 90];
const DONUT_SIZE = 160;

interface Props {
  days: HealthDayResponse[]; // /health/trends response covering at least the longest range
  end: string; // YYYY-MM-DD, last night included
}

export function SleepLengthPieChart({ days, end }: Props) {
  const [range, setRange] = useState<HealthRange>(30);
  const breakdown = useMemo(() => buildSleepBreakdown(days, range, end), [days, range, end]);

  if (!hasAnyHealthData(days)) {
    return (
      <View className="bg-white/35 rounded-xl p-5 mt-4">
        <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
          No Apple Health data yet
        </Text>
        <Text className="text-remetra-muted text-center text-sm">
          Once your sleep syncs from Apple Health, you&apos;ll see how your nights add up here.
        </Text>
      </View>
    );
  }

  // Zero-count slices are left out of the pie but stay in the legend
  const slices = breakdown.buckets
    .filter((b) => b.count > 0)
    .map((b) => ({ x: b.label, y: b.count, fill: BUCKET_COLORS[b.key] }));

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Sleep Length</Text>
      <Text className="text-center text-xs text-gray-500 mb-3">How long you slept each night</Text>

      <SegmentedControl
        options={RANGES.map((r) => ({ value: r, label: `${r} days` }))}
        selected={range}
        onSelect={setRange}
      />

      {breakdown.nightsTracked === 0 ? (
        <View style={{ height: DONUT_SIZE, justifyContent: 'center' }}>
          <Text className="text-remetra-muted text-center text-sm">No sleep data in the last {range} days.</Text>
        </View>
      ) : (
        <View
          className="flex-row items-center mt-3"
          accessible
          accessibilityLabel={`Sleep length over the last ${range} nights: ${breakdown.buckets
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
              <Text className="text-2xl font-semibold text-remetra-espresso">{breakdown.nightsTracked}</Text>
              <Text style={{ fontSize: 10, color: '#666' }}>of {breakdown.totalNights} nights</Text>
            </View>
          </View>

          {/* Legend with counts */}
          <View className="flex-1 ml-4 gap-2">
            {breakdown.buckets.map((b) => (
              <View key={b.key} className="flex-row items-center">
                <View
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 2,
                    backgroundColor: BUCKET_COLORS[b.key],
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
