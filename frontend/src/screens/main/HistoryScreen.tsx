import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { ClipboardList } from 'lucide-react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { FoodCard } from '../../components/FoodCard';
import { LoggingCalendar } from '../../components/LoggingCalendar';
import { SymptomCard } from '../../components/SymptomCard';
import { useBankStore } from '../../store/bankStore';
import { useCalendarStore } from '../../store/calendarStore';
import { useUIStore } from '../../store/uiStore';
import { TimelineEntry } from '../../types/timeline';
import { monthOf } from '../../utils/calendarGrid';
import { addDays, parseDayKey, toDayKey } from '../../utils/dayKey';
import { toTimelineEntries } from '../../utils/timelineEntries';

// ─── screen-local helpers ─────────────────────────────────────────────────────

function formatDayHeader(day: string, today: string): string {
  if (day === today) return 'Today';
  if (day === addDays(today, -1)) return 'Yesterday';
  return parseDayKey(day).toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
}

/** Today's current time moved onto `day`, so a past day starts at a sensible time and today is never in the future. */
function timestampForDay(day: string): Date {
  const now = new Date();
  const date = parseDayKey(day);
  date.setHours(now.getHours(), now.getMinutes(), 0, 0);
  return date > now ? now : date;
}

// ─── screen ───────────────────────────────────────────────────────────────────

export function HistoryScreen() {
  const { foods, symptoms, fetchFoods, fetchSymptoms, scannedFood } = useBankStore();
  const openLogModal = useUIStore((s) => s.openLogModal);
  const logVersion = useUIStore((s) => s.logVersion);
  const { months, days, loadMonth, loadDay, prefetchAround, refresh } = useCalendarStore();

  useEffect(() => {
    if (scannedFood) {
      openLogModal('food');
    }
  }, [scannedFood, openLogModal]);

  const today = toDayKey(new Date());
  const [month, setMonth] = useState(() => monthOf(today));
  const [selectedDay, setSelectedDay] = useState(today);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Card edits shown right away, until the refetch after the edit replaces them
  const [edits, setEdits] = useState<Record<string, Partial<TimelineEntry>>>({});

  const monthData = months[month];
  const dayData = days[selectedDay];

  const entries = useMemo(() => {
    if (!dayData) return [];
    return toTimelineEntries(dayData.food_logs, dayData.symptom_logs, foods, symptoms).map((e) =>
      edits[e.id] ? ({ ...e, ...edits[e.id] } as TimelineEntry) : e
    );
  }, [dayData, foods, symptoms, edits]);

  useEffect(() => {
    setEdits({});
  }, [dayData]);

  const run = useCallback(async (work: () => Promise<void>) => {
    setError(null);
    try {
      await work();
    } catch {
      setError('Failed to load logs. Pull down to retry.');
    }
  }, []);

  const loadVisible = useCallback(
    () =>
      run(async () => {
        const fetchPromises: Promise<void>[] = [];
        if (useBankStore.getState().foods.length === 0) fetchPromises.push(fetchFoods());
        if (useBankStore.getState().symptoms.length === 0) fetchPromises.push(fetchSymptoms());
        await Promise.all([...fetchPromises, loadMonth(month), loadDay(selectedDay)]);
        prefetchAround(month);
      }),
    [run, fetchFoods, fetchSymptoms, loadMonth, loadDay, prefetchAround, month, selectedDay]
  );

  useEffect(() => {
    setLoading(true);
    loadVisible().finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // A new log can land on any day, so refetch what's on screen
  useEffect(() => {
    if (logVersion === 0) return;
    run(() => refresh(month, selectedDay));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [logVersion]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchFoods();
    await fetchSymptoms();
    await run(() => refresh(month, selectedDay));
    setRefreshing(false);
  }, [fetchFoods, fetchSymptoms, run, refresh, month, selectedDay]);

  const changeMonth = useCallback(
    (next: string) => {
      // Select a day in the new month, so the grid and the list always show the same month:
      // today in the current month, otherwise the 1st
      const day = next === monthOf(today) ? today : `${next}-01`;
      setMonth(next);
      setSelectedDay(day);
      run(async () => {
        await Promise.all([loadMonth(next), loadDay(day)]);
        prefetchAround(next);
      });
    },
    [run, loadMonth, loadDay, prefetchAround, today]
  );

  const selectDay = useCallback(
    (day: string) => {
      setSelectedDay(day);
      run(() => loadDay(day));
    },
    [run, loadDay]
  );

  const updateEntry = useCallback(
    (entry: TimelineEntry, patch: Partial<TimelineEntry>) => {
      // Show the edit right away, then refetch so the grid and list match what was saved
      // (a new time can move the log to another day)
      setEdits((prev) => ({ ...prev, [entry.id]: { ...prev[entry.id], ...patch } }));
      run(() => refresh(month, selectedDay));
    },
    [run, refresh, month, selectedDay]
  );

  const hasNoLogsEver = monthData !== undefined && monthData.longest_streak === 0;

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <View className="flex-1 pt-[60px]">

        {/* Header */}
        <View className="flex-row items-center justify-between px-5 mb-4">
          <Text className="text-2xl font-semibold text-remetra-mauve italic tracking-[1px]">
            YOUR HISTORY
          </Text>
          <TouchableOpacity
            onPress={() => openLogModal('select_type', timestampForDay(selectedDay))}
            accessibilityLabel={`Add log for ${formatDayHeader(selectedDay, today)}`}
            style={{
              backgroundColor: '#B8624F',
              borderRadius: 20,
              paddingHorizontal: 14,
              paddingVertical: 8,
              flexDirection: 'row',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Text className="text-white text-base font-semibold">+</Text>
            <Text className="text-white text-[13px] font-medium">Add Log</Text>
          </TouchableOpacity>
        </View>

        {loading && !monthData ? (
          <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#b2939b" /* remetra-mauve */ />
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 40 }}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#b2939b" />
            }
            keyboardShouldPersistTaps="handled"
          >
            <LoggingCalendar
              month={month}
              data={monthData}
              today={today}
              selectedDay={selectedDay}
              onSelectDay={selectDay}
              onChangeMonth={changeMonth}
            />

            {error ? (
              <View className="items-center p-6">
                <Text className="text-remetra-rose text-center mb-4">{error}</Text>
                <TouchableOpacity
                  onPress={() => { setLoading(true); loadVisible().finally(() => setLoading(false)); }}
                  className="bg-remetra-burgundy px-6 py-2.5 rounded-[20px]"
                >
                  <Text className="text-white font-semibold">Retry</Text>
                </TouchableOpacity>
              </View>
            ) : hasNoLogsEver ? (
              <View className="items-center p-6">
                <ClipboardList size={56} color="#b2939b" strokeWidth={1.5} style={{ marginBottom: 12 }} />
                <Text className="text-lg text-remetra-mauve font-semibold text-center">No logs yet</Text>
                <Text className="text-sm text-remetra-mauve text-center mt-2">
                  Tap + Add Log to record your first food or symptom entry.
                </Text>
              </View>
            ) : (
              <View>
                <View className="flex-row items-center mb-3 mt-2">
                  <Text className="text-sm text-remetra-warm-brown mr-2">{formatDayHeader(selectedDay, today)}</Text>
                  <View className="flex-1 h-px bg-white" />
                  {dayData && (
                    <Text className="text-xs text-remetra-warm-brown ml-2">
                      {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
                    </Text>
                  )}
                </View>

                {!dayData ? (
                  <ActivityIndicator size="small" color="#b2939b" style={{ marginTop: 12 }} />
                ) : entries.length === 0 ? (
                  <View className="items-center mt-2">
                    <Text className="text-sm text-remetra-mauve text-center">Nothing logged on this day.</Text>
                    <TouchableOpacity
                      onPress={() => openLogModal('select_type', timestampForDay(selectedDay))}
                      accessibilityRole="button"
                      hitSlop={8}
                    >
                      <Text className="text-sm text-remetra-burgundy font-semibold mt-2">
                        + Log for {formatDayHeader(selectedDay, today)}
                      </Text>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <>
                    <Text className="text-xs text-remetra-mauve mb-2">Tap a card to edit</Text>
                    {entries.map((entry) =>
                      entry.type === 'food' ? (
                        <FoodCard key={entry.id} entry={entry} onUpdate={(patch) => updateEntry(entry, patch)} />
                      ) : (
                        <SymptomCard key={entry.id} entry={entry} onUpdate={(patch) => updateEntry(entry, patch)} />
                      )
                    )}
                  </>
                )}
              </View>
            )}
          </ScrollView>
        )}
      </View>
    </View>
  );
}
