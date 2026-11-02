/**
 * Month calendar of how completely each day was logged. Cells use the same size, gap, radius and
 * outline as the health calendar. Each cell is split on the diagonal: food fills the top-left
 * triangle, a symptom the bottom-right. Status never relies on color alone: logged days also carry
 * the log modal's icons (fork and knife for food, stethoscope for a symptom, both when fully
 * logged), empty days are outlined, and every cell has a screen-reader label. The marks only say
 * what was logged; nothing celebrates a day or hints at how bad the symptoms were.
 */
import { useMemo } from 'react';
import { ActivityIndicator, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import Svg, { Polygon } from 'react-native-svg';
import { ChevronLeft, ChevronRight, Flame, Stethoscope, Utensils, type LucideIcon } from 'lucide-react-native';
import type { CalendarDayResponse, CalendarMonthResponse, DayStatus } from '../api/calendar_service';
import { buildCalendarGrid, CalendarCell, monthOf, monthRange, shiftMonth } from '../utils/calendarGrid';
import { parseDayKey } from '../utils/dayKey';

const WEEKDAY_HEADERS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
const GAP = 3;
const MAX_CELL = 40;
const EMPTY_BORDER = '#d8d6d0';
const SELECTED_BORDER = '#5C2E14'; // remetra-espresso
const FOOD_COLOR = '#fca450'; // remetra-orange, same as FoodCard
const SYMPTOM_COLOR = '#b2939b'; // remetra-mauve, same as SymptomCard
const MARK_COLOR = '#5C2E14'; // remetra-espresso, readable on both fills and on white

const STATUS_ICONS: Record<DayStatus, LucideIcon[]> = {
  complete: [Utensils, Stethoscope],
  food_only: [Utensils],
  symptoms_only: [Stethoscope],
  empty: [],
};

const STATUS_LABELS: Record<DayStatus, string> = {
  complete: 'fully logged',
  food_only: 'food only',
  symptoms_only: 'symptoms only',
  empty: 'nothing logged',
};

interface Props {
  month: string; // YYYY-MM
  data: CalendarMonthResponse | undefined; // undefined while the month loads
  today: string;
  selectedDay: string;
  onSelectDay: (day: string) => void;
  onChangeMonth: (month: string) => void;
}

/** Diagonal fill: food is the top-left triangle, symptom the bottom-right. Sizes are inside any border. */
function StatusFill({ status, width, height = width }: { status: DayStatus; width: number; height?: number }) {
  const food = status === 'complete' || status === 'food_only';
  const symptom = status === 'complete' || status === 'symptoms_only';
  if (!food && !symptom) return null;
  return (
    <Svg width={width} height={height} style={{ position: 'absolute', top: 0, left: 0 }}>
      {food && <Polygon points={`0,0 ${width},0 0,${height}`} fill={FOOD_COLOR} />}
      {symptom && <Polygon points={`${width},0 ${width},${height} 0,${height}`} fill={SYMPTOM_COLOR} />}
    </Svg>
  );
}

function StatusMark({ status, size }: { status: DayStatus; size: number }) {
  const icons = STATUS_ICONS[status];
  if (icons.length === 0) return null;
  return (
    <View style={{ flexDirection: 'row', gap: 1 }}>
      {icons.map((Icon, i) => (
        <Icon key={i} size={size} color={MARK_COLOR} strokeWidth={2.25} />
      ))}
    </View>
  );
}

function LegendItem({ status, label }: { status: DayStatus; label: string }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
      <View
        style={{
          width: status === 'complete' ? 24 : 16,
          height: 16,
          borderRadius: 3,
          overflow: 'hidden',
          borderWidth: status === 'empty' ? 1 : 0,
          borderColor: EMPTY_BORDER,
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <StatusFill status={status} width={status === 'complete' ? 24 : 16} height={16} />
        <StatusMark status={status} size={10} />
      </View>
      <Text style={{ fontSize: 11, color: '#666' }}>{label}</Text>
    </View>
  );
}

export function LoggingCalendar({ month, data, today, selectedDay, onSelectDay, onChangeMonth }: Props) {
  const { width } = useWindowDimensions();
  // Screen has 20px padding each side, card has 16px (p-4) each side
  const contentWidth = width - 40 - 32;
  const cellSize = Math.min(MAX_CELL, Math.floor((contentWidth - GAP * 6) / 7));

  const grid = useMemo(() => {
    const byDate = new Map(data?.days.map((d) => [d.date, d]));
    return buildCalendarGrid(monthRange(month), (day) => byDate.get(day) ?? null);
  }, [month, data]);

  const canGoForward = month < monthOf(today);
  const monthTitle = parseDayKey(`${month}-01`).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const renderCell = (c: CalendarCell<CalendarDayResponse>, col: number) => {
    const base = { width: cellSize, height: cellSize, borderRadius: 3, marginRight: col < 6 ? GAP : 0 };
    if (!c.inRange) return <View key={col} style={base} />;

    const status = c.data?.status ?? 'empty';
    const isFuture = c.day > today;
    const isToday = c.day === today;
    const isSelected = c.day === selectedDay;
    const dateLabel = c.date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
    const borderWidth = isSelected ? 2 : status === 'empty' ? 1 : 0;
    // Two icons share the width on fully logged days
    const markSize = Math.max(8, Math.round(cellSize * (status === 'complete' ? 0.26 : 0.3)));

    return (
      <TouchableOpacity
        key={col}
        disabled={isFuture}
        onPress={() => onSelectDay(c.day)}
        accessibilityRole="button"
        accessibilityState={{ selected: isSelected, disabled: isFuture }}
        accessibilityLabel={`${dateLabel}${isToday ? ', today' : ''}, ${isFuture ? 'upcoming' : STATUS_LABELS[status]}`}
        style={{
          ...base,
          overflow: 'hidden',
          backgroundColor: '#fff',
          borderWidth,
          borderColor: isSelected ? SELECTED_BORDER : EMPTY_BORDER,
          alignItems: 'center',
          justifyContent: 'center',
          opacity: isFuture ? 0.4 : 1,
        }}
      >
        <StatusFill status={status} width={cellSize - borderWidth * 2} />
        <Text
          style={{
            fontSize: 11,
            lineHeight: 13,
            color: '#5C2E14',
            fontWeight: isToday ? '700' : '400',
            textDecorationLine: isToday ? 'underline' : 'none',
          }}
        >
          {c.date.getDate()}
        </Text>
        {!isFuture && <StatusMark status={status} size={markSize} />}
      </TouchableOpacity>
    );
  };

  return (
    <View className="bg-white rounded-2xl p-4 mb-4">
      {/* Month navigation */}
      <View className="flex-row items-center justify-between mb-2">
        <TouchableOpacity
          onPress={() => onChangeMonth(shiftMonth(month, -1))}
          accessibilityRole="button"
          accessibilityLabel="Previous month"
          hitSlop={8}
        >
          <ChevronLeft size={22} color="#5C2E14" />
        </TouchableOpacity>
        <View className="flex-row items-center gap-2">
          <Text className="text-lg font-semibold text-remetra-espresso">{monthTitle}</Text>
          {!data && <ActivityIndicator size="small" color="#b2939b" />}
        </View>
        <TouchableOpacity
          onPress={() => onChangeMonth(shiftMonth(month, 1))}
          disabled={!canGoForward}
          accessibilityRole="button"
          accessibilityLabel="Next month"
          accessibilityState={{ disabled: !canGoForward }}
          hitSlop={8}
          style={{ opacity: canGoForward ? 1 : 0.3 }}
        >
          <ChevronRight size={22} color="#5C2E14" />
        </TouchableOpacity>
      </View>

      {/* Streak */}
      <View className="flex-row items-center justify-center gap-1 mb-3" style={{ minHeight: 18 }} accessible>
        {data && (
          <>
            <Flame size={14} color="#B8624F" />
            <Text className="text-xs text-remetra-warm-brown">
              {data.current_streak}-day streak · Best {data.longest_streak}
            </Text>
          </>
        )}
      </View>

      {/* Calendar grid */}
      <View className="self-center">
        <View style={{ flexDirection: 'row', marginBottom: 2 }}>
          {WEEKDAY_HEADERS.map((label, i) => (
            <Text
              key={i}
              style={{ width: cellSize, marginRight: i < 6 ? GAP : 0, fontSize: 9, color: '#666', textAlign: 'center' }}
            >
              {label}
            </Text>
          ))}
        </View>
        {grid.weeks.map((week, row) => (
          <View key={row} style={{ flexDirection: 'row', marginBottom: row < grid.weeks.length - 1 ? GAP : 0 }}>
            {week.map(renderCell)}
          </View>
        ))}
      </View>

      {/* Legend */}
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', columnGap: 12, rowGap: 6, marginTop: 12 }}>
        <LegendItem status="complete" label="Food + symptom" />
        <LegendItem status="food_only" label="Food only" />
        <LegendItem status="symptoms_only" label="Symptoms only" />
        <LegendItem status="empty" label="Nothing logged" />
      </View>
    </View>
  );
}
