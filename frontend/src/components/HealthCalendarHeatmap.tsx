/**
 * SAMPLE 3 of 3 — Health calendar heatmap (live on AnalysisScreen, below Sample 2).
 *
 * Design: a wall-calendar grid (rows = weeks, oldest at the top; columns = Mon–Sun) for the selected metric
 * (Sleep / HRV / Resting HR toggle) over a 7 / 30 / 90-day range, same controls as Samples 1 and 2.
 * Each day is shaded by the same value bands and one-hue ramps as Sample 2, so a color means the
 * same thing in both and never shifts with the range. Days with no reading are empty outlined
 * cells, symptom days carry a dot, and tapping a day shows its exact value.
 */
import { useMemo, useState } from 'react';
import { View, Text, TouchableOpacity, useWindowDimensions } from 'react-native';
import type { HealthDayResponse } from '../api/health_service';
import { SegmentedControl } from './SegmentedControl';
import {
  bandLabels,
  buildCalendarGrid,
  hasAnyHealthData,
  CalendarCell,
  HealthMetric,
  HealthRange,
} from '../utils/healthChartData';

// Validated ordinal ramps (one hue, light -> dark), shared with Sample 2; no red
const METRICS: {
  key: HealthMetric;
  label: string;
  subtitle: string;
  ramp: [string, string, string, string];
}[] = [
  { key: 'sleep', label: 'Sleep', subtitle: 'Hours asleep each night', ramp: ['#86b6ef', '#3987e5', '#1c5cab', '#0d366b'] },
  { key: 'hrv', label: 'HRV', subtitle: 'Heart rate variability each day', ramp: ['#5cc79f', '#1f9e70', '#13734f', '#0b4a33'] },
  { key: 'restingHr', label: 'Resting HR', subtitle: 'Resting heart rate each day', ramp: ['#a79ef0', '#7a6de2', '#5443c4', '#33278a'] },
];

const RANGES: HealthRange[] = [7, 30, 90];
const WEEKDAY_HEADERS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
const MONTH_LABEL_WIDTH = 28;
const GAP = 3;
const MAX_CELL = 32;
const EMPTY_BORDER = '#d8d6d0';
const SYMPTOM_DOT_COLOR = '#b2939b';
const SELECTED_BORDER = '#5C2E14';

interface Props {
  days: HealthDayResponse[]; // /health/trends response covering at least the longest range
  end: string; // YYYY-MM-DD, last day shown
}

function formatValue(metric: HealthMetric, value: number | null): string {
  if (value === null) return 'No data';
  if (metric === 'sleep') return `${value}h`;
  return metric === 'hrv' ? `${value} ms` : `${value} bpm`;
}

function formatDate(d: Date): string {
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

export function HealthCalendarHeatmap({ days, end }: Props) {
  const { width } = useWindowDimensions();
  // Screen has 24px padding each side, card has 16px (p-4) each side
  const contentWidth = width - 48 - 32;

  const [metric, setMetric] = useState<HealthMetric>('sleep');
  const [range, setRange] = useState<HealthRange>(30);
  const [selected, setSelected] = useState<CalendarCell | null>(null);

  const grid = useMemo(() => buildCalendarGrid(days, metric, range, end), [days, metric, range, end]);

  if (!hasAnyHealthData(days)) {
    return (
      <View className="bg-white/35 rounded-xl p-5 mt-4">
        <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
          No Apple Health data yet
        </Text>
        <Text className="text-remetra-muted text-center text-sm">
          Once your sleep, HRV, and resting heart rate sync from Apple Health, your days will fill in here.
        </Text>
      </View>
    );
  }

  const meta = METRICS.find((m) => m.key === metric)!;
  const weekCount = grid.weeks.length;
  const cellSize = Math.min(MAX_CELL, Math.floor((contentWidth - MONTH_LABEL_WIDTH - GAP * 6) / 7));
  const dotSize = Math.max(5, Math.round(cellSize * 0.3));
  const hasMetricData = grid.weeks.some((w) => w.some((c) => c.band !== null));

  const renderCell = (c: CalendarCell, key: number, marginRight: number) => {
    const base = { width: cellSize, height: cellSize, borderRadius: 3, marginRight };
    if (!c.inRange) return <View key={key} style={base} />;

    const isSelected = selected !== null && selected.date.getTime() === c.date.getTime();
    return (
      <TouchableOpacity
        key={key}
        onPress={() => setSelected(isSelected ? null : c)}
        accessibilityRole="button"
        accessibilityLabel={`${formatDate(c.date)}: ${formatValue(metric, c.value)}${c.hasSymptom ? ', symptom logged' : ''}`}
        style={{
          ...base,
          backgroundColor: c.band !== null ? meta.ramp[c.band] : '#fff',
          borderWidth: isSelected ? 2 : c.band === null ? 1 : 0,
          borderColor: isSelected ? SELECTED_BORDER : EMPTY_BORDER,
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {c.hasSymptom && (
          <View
            style={{
              width: dotSize,
              height: dotSize,
              borderRadius: dotSize / 2,
              backgroundColor: SYMPTOM_DOT_COLOR,
              borderWidth: 1.5,
              borderColor: '#fff',
            }}
          />
        )}
      </TouchableOpacity>
    );
  };

  const changeMetric = (m: HealthMetric) => {
    setMetric(m);
    setSelected(null);
  };
  const changeRange = (r: HealthRange) => {
    setRange(r);
    setSelected(null);
  };

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-1">Health Calendar</Text>
      <Text className="text-center text-xs text-gray-500 mb-3">{meta.subtitle}</Text>

      <SegmentedControl
        options={METRICS.map((m) => ({ value: m.key, label: m.label }))}
        selected={metric}
        onSelect={changeMetric}
      />
      <View className="h-2" />
      <SegmentedControl
        options={RANGES.map((r) => ({ value: r, label: `${r} days` }))}
        selected={range}
        onSelect={changeRange}
      />

      {!hasMetricData && (
        <Text className="text-remetra-muted text-center text-sm mt-3">
          No {meta.label} data in the last {range} days.
        </Text>
      )}

      {/* Calendar grid */}
      <View className="mt-3 self-center">
        {/* Weekday headers */}
        <View style={{ flexDirection: 'row', marginLeft: MONTH_LABEL_WIDTH, marginBottom: 2 }}>
          {WEEKDAY_HEADERS.map((label, i) => (
            <Text
              key={i}
              style={{ width: cellSize, marginRight: i < 6 ? GAP : 0, fontSize: 9, color: '#666', textAlign: 'center' }}
            >
              {label}
            </Text>
          ))}
        </View>

        {/* One row per week, oldest at the top */}
        {grid.weeks.map((week, row) => (
          <View key={row} style={{ flexDirection: 'row', marginBottom: row < weekCount - 1 ? GAP : 0 }}>
            <View style={{ width: MONTH_LABEL_WIDTH, justifyContent: 'center' }}>
              <Text style={{ fontSize: 9, color: '#666' }}>{grid.monthLabels[row] ?? ''}</Text>
            </View>
            {week.map((c, col) => renderCell(c, col, col < 6 ? GAP : 0))}
          </View>
        ))}
      </View>

      {/* Tapped-day detail */}
      <Text className="text-center text-sm text-remetra-espresso mt-3" style={{ minHeight: 20 }}>
        {selected
          ? `${formatDate(selected.date)} · ${formatValue(metric, selected.value)}${selected.hasSymptom ? ' · Symptom logged' : ''}`
          : 'Tap a day to see its value'}
      </Text>

      {/* Legend */}
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', columnGap: 12, rowGap: 6, marginTop: 8 }}>
        {bandLabels(metric).map((label, i) => (
          <View key={label} style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
            <View style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: meta.ramp[i] }} />
            <Text style={{ fontSize: 11, color: '#666' }}>{label}</Text>
          </View>
        ))}
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 10, height: 10, borderRadius: 2, borderWidth: 1, borderColor: EMPTY_BORDER }} />
          <Text style={{ fontSize: 11, color: '#666' }}>No data</Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: SYMPTOM_DOT_COLOR }} />
          <Text style={{ fontSize: 11, color: '#666' }}>Symptom logged</Text>
        </View>
      </View>
    </View>
  );
}
