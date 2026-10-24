import { useMemo, useState } from 'react';
import { VictoryChart, VictoryLine, VictoryScatter, VictoryBar, VictoryAxis } from 'victory-native';
import { View, Text, TouchableOpacity, useWindowDimensions } from 'react-native';
import {
  buildHealthTrends,
  summarizeMetric,
  parseDayKey,
  HealthDayResponse,
  HealthMetricKey,
  HealthTrendPoint,
} from '../api/health_service';

// Validated (dataviz palette check) for lightness, chroma, and colorblind separation.
// Each metric gets its own panel + title, so identity never rests on color alone.
const METRICS: { key: HealthMetricKey; label: string; unit: string; color: string }[] = [
  { key: 'sleep', label: 'Sleep', unit: 'h', color: '#2a78d6' },
  { key: 'hrv', label: 'HRV', unit: 'ms', color: '#1baf7a' },
  { key: 'restingHr', label: 'Resting HR', unit: 'bpm', color: '#eb6834' },
];

const SYMPTOM_BAND_COLOR = '#b2939b';
const PANEL_HEIGHT = 110;
const AXIS_HEIGHT = 24;
const PADDING_LEFT = 32;
const PADDING_RIGHT = 12;

interface SymptomLog {
  timestamp: string;
}

interface Props {
  healthDays: HealthDayResponse[];
  symptomLogs: SymptomLog[];
  start: string; // YYYY-MM-DD
  end: string;   // YYYY-MM-DD
}

function formatTick(d: Date): string {
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatValue(value: number | null, unit: string): string {
  return value === null ? '—' : `${value}${unit === 'h' ? 'h' : ` ${unit}`}`;
}

function yDomain(points: HealthTrendPoint[]): [number, number] {
  const values = points.map((p) => p.y).filter((y): y is number => y !== null);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = Math.max((max - min) * 0.15, max * 0.05, 1);
  return [Math.max(0, Math.floor(min - pad)), Math.ceil(max + pad)];
}

export function HealthTrendsChart({ healthDays, symptomLogs, start, end }: Props) {
  const { width } = useWindowDimensions();
  // Screen has 24px padding each side, card has 16px (p-4) each side
  const chartWidth = width - 48 - 32;

  const [enabled, setEnabled] = useState<Record<HealthMetricKey, boolean>>({
    sleep: true,
    hrv: true,
    restingHr: true,
  });

  const trends = useMemo(
    () => buildHealthTrends(healthDays, symptomLogs, start, end),
    [healthDays, symptomLogs, start, end],
  );

  const anyData = trends.hasData.sleep || trends.hasData.hrv || trends.hasData.restingHr;

  if (!anyData) {
    return (
      <View className="bg-white/35 rounded-xl p-5 mt-4">
        <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
          No Apple Health data yet
        </Text>
        <Text className="text-remetra-muted text-center text-sm">
          Once your sleep, HRV, and resting heart rate sync from Apple Health, they&apos;ll show up here next to the days
          you logged symptoms.
        </Text>
      </View>
    );
  }

  const visible = METRICS.filter((m) => enabled[m.key]);
  const xDomain: [Date, Date] = [parseDayKey(start), parseDayKey(end)];
  const plotWidth = chartWidth - PADDING_LEFT - PADDING_RIGHT;
  const bandWidth = Math.max(2, (plotWidth / trends.days.length) * 0.85);

  // ~5 evenly spaced date ticks across the range
  const tickCount = Math.min(5, trends.days.length);
  const tickStep = Math.max(1, Math.floor((trends.days.length - 1) / Math.max(1, tickCount - 1)));
  const tickValues = trends.days.filter((_, i) => i % tickStep === 0).map(parseDayKey);

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Health Trends</Text>
      <Text className="text-center text-xs text-gray-500 mb-3">
        Daily Apple Health data with your symptom days shaded
      </Text>

      {/* Metric toggles */}
      <View className="flex-row flex-wrap justify-center gap-2 mb-2">
        {METRICS.map((m) => {
          const on = enabled[m.key];
          return (
            <TouchableOpacity
              key={m.key}
              accessibilityRole="switch"
              accessibilityState={{ checked: on }}
              accessibilityLabel={`Show ${m.label}`}
              onPress={() => setEnabled((prev) => ({ ...prev, [m.key]: !prev[m.key] }))}
              className={`flex-row items-center rounded-full py-1.5 px-3 gap-1.5 border ${
                on ? 'bg-remetra-surface-accent border-remetra-accent' : 'bg-white border-remetra-border'
              }`}
            >
              <View
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: on ? m.color : 'transparent',
                  borderWidth: 1.5,
                  borderColor: m.color,
                }}
              />
              <Text className={`text-xs ${on ? 'text-remetra-espresso font-semibold' : 'text-remetra-muted'}`}>
                {m.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Symptom-day key */}
      <View className="flex-row items-center justify-center gap-1.5 mb-2">
        <View style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: SYMPTOM_BAND_COLOR, opacity: 0.35 }} />
        <Text style={{ fontSize: 11, color: '#666' }}>
          Symptom logged ({trends.symptomDays.length} {trends.symptomDays.length === 1 ? 'day' : 'days'})
        </Text>
      </View>

      {visible.length === 0 ? (
        <Text className="text-remetra-muted text-center text-sm my-6">
          Turn on a metric above to see its trend.
        </Text>
      ) : (
        visible.map((m, i) => {
          const points = trends.series[m.key];
          const isLast = i === visible.length - 1;
          const height = PANEL_HEIGHT + (isLast ? AXIS_HEIGHT : 0);

          if (!trends.hasData[m.key]) {
            return (
              <View key={m.key} className="mt-2">
                <PanelHeader label={m.label} color={m.color} />
                <View style={{ height: PANEL_HEIGHT / 2, justifyContent: 'center' }}>
                  <Text className="text-remetra-muted text-center text-xs">
                    No {m.label} data in this period.
                  </Text>
                </View>
              </View>
            );
          }

          const [yMin, yMax] = yDomain(points);
          const summary = summarizeMetric(points, trends.symptomDays);
          const bands = trends.symptomDays.map((d) => ({ x: parseDayKey(d), y: yMax, y0: yMin }));
          const readings = points.filter((p) => p.y !== null);

          return (
            <View key={m.key} className="mt-2">
              <PanelHeader
                label={m.label}
                color={m.color}
                detail={
                  trends.symptomDays.length > 0
                    ? `Symptom days ${formatValue(summary.symptomDayAvg, m.unit)} · other days ${formatValue(summary.otherDayAvg, m.unit)}`
                    : `Avg ${formatValue(summary.otherDayAvg, m.unit)}`
                }
              />
              <VictoryChart
                width={chartWidth}
                height={height}
                scale={{ x: 'time' }}
                domain={{ x: xDomain, y: [yMin, yMax] }}
                domainPadding={{ x: bandWidth / 2 }}
                padding={{ left: PADDING_LEFT, right: PADDING_RIGHT, top: 6, bottom: isLast ? AXIS_HEIGHT : 6 }}
              >
                <VictoryAxis
                  tickValues={tickValues}
                  tickFormat={(t: Date) => (isLast ? formatTick(new Date(t)) : '')}
                  style={{
                    tickLabels: { fontSize: 9, fill: '#666', padding: 4 },
                    axis: { stroke: '#ddd' },
                    ticks: { stroke: 'transparent' },
                    grid: { stroke: 'transparent' },
                  }}
                />
                <VictoryAxis
                  dependentAxis
                  tickCount={3}
                  style={{
                    tickLabels: { fontSize: 9, fill: '#666', padding: 3 },
                    axis: { stroke: 'transparent' },
                    grid: { stroke: '#f0f0f0' },
                  }}
                />
                {bands.length > 0 && (
                  <VictoryBar
                    data={bands}
                    barWidth={bandWidth}
                    style={{ data: { fill: SYMPTOM_BAND_COLOR, opacity: 0.25 } }}
                  />
                )}
                {/* null y values render as gaps, so missing days are never interpolated */}
                <VictoryLine data={points} style={{ data: { stroke: m.color, strokeWidth: 2 } }} />
                {/* Dots keep isolated readings (surrounded by gaps) visible */}
                <VictoryScatter
                  data={readings}
                  size={2.5}
                  style={{ data: { fill: m.color, stroke: '#fff', strokeWidth: 1 } }}
                />
              </VictoryChart>
            </View>
          );
        })
      )}
    </View>
  );
}

function PanelHeader({ label, color, detail }: { label: string; color: string; detail?: string }) {
  return (
    <View className="flex-row items-center justify-between px-1">
      <View className="flex-row items-center gap-1.5">
        <View style={{ width: 10, height: 2, borderRadius: 1, backgroundColor: color }} />
        <Text className="text-sm font-semibold text-remetra-espresso">{label}</Text>
      </View>
      {detail ? <Text style={{ fontSize: 10, color: '#666' }}>{detail}</Text> : null}
    </View>
  );
}
