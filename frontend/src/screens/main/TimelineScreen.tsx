import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { FoodCard } from '../../components/FoodCard';
import { SymptomCard } from '../../components/SymptomCard';
import { foodLogService, FoodLogResponse } from '../../api/food_log_service';
import { symptomLogService, SymptomLogResponse } from '../../api/symptom_log_service';
import { useBankStore } from '../../store/bankStore';
import { useUIStore } from '../../store/uiStore';
import { TimelineEntry, FoodTimelineEntry, SymptomTimelineEntry } from '../../types/timeline';

// ─── screen-local helpers ─────────────────────────────────────────────────────

function formatDateHeader(date: Date): string {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  const sameDay = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
  if (sameDay(date, today)) return 'Today';
  if (sameDay(date, yesterday)) return 'Yesterday';
  return date.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
}

function groupByDate(entries: TimelineEntry[]): { dateKey: string; label: string; items: TimelineEntry[] }[] {
  const map = new Map<string, { label: string; items: TimelineEntry[] }>();
  for (const entry of entries) {
    const d = entry.timestamp;
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (!map.has(key)) map.set(key, { label: formatDateHeader(d), items: [] });
    map.get(key)!.items.push(entry);
  }
  return Array.from(map.entries()).map(([dateKey, val]) => ({ dateKey, ...val }));
}

// ─── screen ───────────────────────────────────────────────────────────────────

export function TimelineScreen() {
  const { foods, symptoms, fetchFoods, fetchSymptoms } = useBankStore();
  const openLogModal = useUIStore((s) => s.openLogModal);

  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const fetchPromises: Promise<void>[] = [];
      if (foods.length === 0) fetchPromises.push(fetchFoods());
      if (symptoms.length === 0) fetchPromises.push(fetchSymptoms());
      await Promise.all(fetchPromises);

      const [foodLogs, symptomLogs] = await Promise.all([
        foodLogService.getMyFoodLogs(),
        symptomLogService.getMySymptomLogs(),
      ]);

      const { foods: latestFoods, symptoms: latestSymptoms } = useBankStore.getState();
      const foodMap = new Map(latestFoods.map((f) => [f.id, f]));
      const symptomMap = new Map(latestSymptoms.map((s) => [s.id, s]));

      const foodEntries: FoodTimelineEntry[] = foodLogs.map((log: FoodLogResponse) => {
        const food = foodMap.get(log.food_id);
        return {
          type: 'food',
          id: log.id,
          name: food?.name ?? 'Unknown Food',
          ingredients: food?.ingredients ?? [],
          quantity: log.quantity,
          notes: log.notes,
          timestamp: new Date(log.timestamp),
        };
      });

      const symptomEntries: SymptomTimelineEntry[] = symptomLogs.map((log: SymptomLogResponse) => {
        const symptom = symptomMap.get(log.symptom_id);
        return {
          type: 'symptom',
          id: log.id,
          name: symptom?.name ?? 'Unknown Symptom',
          location: symptom?.location ?? '',
          sensation: symptom?.sensation ?? '',
          intensity: log.intensity,
          duration: log.duration,
          notes: log.notes,
          timestamp: new Date(log.timestamp),
        };
      });

      const all = [...foodEntries, ...symptomEntries].sort(
        (a, b) => b.timestamp.getTime() - a.timestamp.getTime()
      );
      setEntries(all);
    } catch {
      setError('Failed to load logs. Pull down to retry.');
    }
  }, [foods, symptoms, fetchFoods, fetchSymptoms]);

  useEffect(() => {
    setLoading(true);
    load().finally(() => setLoading(false));
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchFoods();
    await fetchSymptoms();
    await load();
    setRefreshing(false);
  }, [load, fetchFoods, fetchSymptoms]);

  const updateEntry = useCallback((id: string, patch: Partial<TimelineEntry>) => {
    setEntries((prev) =>
      prev.map((e) => (e.id === id ? ({ ...e, ...patch } as TimelineEntry) : e))
    );
  }, []);

  const groups = groupByDate(entries);

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
            onPress={openLogModal}
            className="bg-remetra-burgundy rounded-[20px] px-3.5 py-2 flex-row items-center gap-1"
          >
            <Text className="text-white text-base font-semibold">+</Text>
            <Text className="text-white text-[13px] font-medium">Add Log</Text>
          </TouchableOpacity>
        </View>

        {/* Legend */}
        <View className="flex-row gap-4 px-5 mb-4">
          <View className="flex-row items-center gap-1.5">
            <View className="w-3 h-3 rounded-full bg-remetra-orange" />
            <Text className="text-xs text-remetra-muted">Food</Text>
          </View>
          <View className="flex-row items-center gap-1.5">
            <View className="w-3 h-3 rounded-full bg-remetra-mauve" />
            <Text className="text-xs text-remetra-muted">Symptom</Text>
          </View>
          <Text className="text-xs text-neutral-300 ml-1">Tap a card to edit</Text>
        </View>

        {/* Content */}
        {loading ? (
          <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#b2939b" /* remetra-mauve */ />
          </View>
        ) : error ? (
          <View className="flex-1 justify-center items-center p-6">
            <Text className="text-remetra-rose text-center mb-4">{error}</Text>
            <TouchableOpacity
              onPress={() => { setLoading(true); load().finally(() => setLoading(false)); }}
              className="bg-remetra-burgundy px-6 py-2.5 rounded-[20px]"
            >
              <Text className="text-white font-semibold">Retry</Text>
            </TouchableOpacity>
          </View>
        ) : entries.length === 0 ? (
          <View className="flex-1 justify-center items-center p-6">
            <Text className="text-5xl mb-3">📋</Text>
            <Text className="text-lg text-remetra-mauve font-semibold text-center">No logs yet</Text>
            <Text className="text-sm text-remetra-muted text-center mt-2">
              Tap + Add Log to record your first food or symptom entry.
            </Text>
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 40 }}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#b2939b" />
            }
            keyboardShouldPersistTaps="handled"
          >
            {groups.map((group) => (
              <View key={group.dateKey}>
                <View className="flex-row items-center mb-3 mt-2">
                  <Text className="text-sm font-bold text-[#7B5B6B] mr-2">{group.label}</Text>
                  <View className="flex-1 h-px bg-neutral-200" />
                  <Text className="text-xs text-remetra-muted ml-2">
                    {group.items.length} {group.items.length === 1 ? 'entry' : 'entries'}
                  </Text>
                </View>

                {group.items.map((entry) =>
                  entry.type === 'food' ? (
                    <FoodCard
                      key={entry.id}
                      entry={entry}
                      onUpdate={(patch) => updateEntry(entry.id, patch)}
                    />
                  ) : (
                    <SymptomCard
                      key={entry.id}
                      entry={entry}
                      onUpdate={(patch) => updateEntry(entry.id, patch)}
                    />
                  )
                )}
              </View>
            ))}
          </ScrollView>
        )}
      </View>
    </View>
  );
}
