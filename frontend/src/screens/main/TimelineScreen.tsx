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
import { foodLogService, FoodLogResponse } from '../../api/food_log_service';
import { symptomLogService, SymptomLogResponse } from '../../api/symptom_log_service';
import { useBankStore } from '../../store/bankStore';
import { useUIStore } from '../../store/uiStore';

// ─── unified entry ──────────────────────────────────────────────────────────

type FoodTimelineEntry = {
  type: 'food';
  id: string;
  name: string;
  ingredients: string[];
  quantity: string | null;
  notes: string | null;
  timestamp: Date;
};

type SymptomTimelineEntry = {
  type: 'symptom';
  id: string;
  name: string;
  location: string;
  sensation: string;
  intensity: number;
  duration: number | null;
  notes: string | null;
  timestamp: Date;
};

type TimelineEntry = FoodTimelineEntry | SymptomTimelineEntry;

// ─── helpers ─────────────────────────────────────────────────────────────────

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

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
    if (!map.has(key)) {
      map.set(key, { label: formatDateHeader(d), items: [] });
    }
    map.get(key)!.items.push(entry);
  }

  return Array.from(map.entries()).map(([dateKey, val]) => ({ dateKey, ...val }));
}

// ─── sub-components ──────────────────────────────────────────────────────────

function FoodCard({ entry }: { entry: FoodTimelineEntry }) {
  return (
    <View
      style={{
        backgroundColor: '#FEF0E7',
        borderLeftWidth: 4,
        borderLeftColor: '#fca450',
        borderRadius: 12,
        padding: 14,
        marginBottom: 10,
      }}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <Text style={{ fontSize: 16 }}>🍽</Text>
            <Text style={{ fontSize: 16, fontWeight: '600', color: '#7C4A1E' }}>{entry.name}</Text>
          </View>
          {entry.quantity ? (
            <Text style={{ fontSize: 13, color: '#A0673A', marginBottom: 2 }}>
              Qty: {entry.quantity}
            </Text>
          ) : null}
          {entry.ingredients.length > 0 && (
            <Text style={{ fontSize: 12, color: '#B07850' }} numberOfLines={2}>
              {entry.ingredients.join(', ')}
            </Text>
          )}
          {entry.notes ? (
            <Text style={{ fontSize: 12, color: '#9E7050', marginTop: 4, fontStyle: 'italic' }}>
              {entry.notes}
            </Text>
          ) : null}
        </View>
        <Text style={{ fontSize: 12, color: '#B07850', marginLeft: 8 }}>{formatTime(entry.timestamp)}</Text>
      </View>
    </View>
  );
}

function SymptomCard({ entry }: { entry: SymptomTimelineEntry }) {
  const intensityColor = entry.intensity >= 7 ? '#C85A4A' : entry.intensity >= 4 ? '#D9806E' : '#b2939b';
  return (
    <View
      style={{
        backgroundColor: '#FBF0F2',
        borderLeftWidth: 4,
        borderLeftColor: intensityColor,
        borderRadius: 12,
        padding: 14,
        marginBottom: 10,
      }}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <Text style={{ fontSize: 16 }}>🩺</Text>
            <Text style={{ fontSize: 16, fontWeight: '600', color: '#7B3B4E' }}>{entry.name}</Text>
          </View>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 2 }}>
            <View
              style={{
                backgroundColor: intensityColor,
                borderRadius: 10,
                paddingHorizontal: 8,
                paddingVertical: 2,
              }}
            >
              <Text style={{ color: 'white', fontSize: 12, fontWeight: '600' }}>
                Intensity {entry.intensity}/10
              </Text>
            </View>
            {entry.duration ? (
              <Text style={{ fontSize: 12, color: '#9E7080' }}>{entry.duration} min</Text>
            ) : null}
          </View>
          {entry.location ? (
            <Text style={{ fontSize: 12, color: '#9E7080' }}>Location: {entry.location}</Text>
          ) : null}
          {entry.sensation ? (
            <Text style={{ fontSize: 12, color: '#9E7080' }}>Sensation: {entry.sensation}</Text>
          ) : null}
          {entry.notes ? (
            <Text style={{ fontSize: 12, color: '#9E7080', marginTop: 4, fontStyle: 'italic' }}>
              {entry.notes}
            </Text>
          ) : null}
        </View>
        <Text style={{ fontSize: 12, color: '#9E7080', marginLeft: 8 }}>{formatTime(entry.timestamp)}</Text>
      </View>
    </View>
  );
}

// ─── main screen ─────────────────────────────────────────────────────────────

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
      // fetch banks if empty
      const fetchPromises: Promise<void>[] = [];
      if (foods.length === 0) fetchPromises.push(fetchFoods());
      if (symptoms.length === 0) fetchPromises.push(fetchSymptoms());
      await Promise.all(fetchPromises);

      const [foodLogs, symptomLogs] = await Promise.all([
        foodLogService.getMyFoodLogs(),
        symptomLogService.getMySymptomLogs(),
      ]);

      // latest food/symptom banks (after fetch above)
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
    } catch (err: any) {
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

  const groups = groupByDate(entries);

  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <View style={{ flex: 1, paddingTop: 60 }}>
        {/* Header */}
        <View
          style={{
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingHorizontal: 20,
            marginBottom: 16,
          }}
        >
          <Text
            style={{
              fontSize: 24,
              fontWeight: '600',
              color: '#b2939b',
              fontStyle: 'italic',
              letterSpacing: 1,
            }}
          >
            YOUR HISTORY
          </Text>
          <TouchableOpacity
            onPress={openLogModal}
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
            <Text style={{ color: 'white', fontSize: 16, fontWeight: '600' }}>+</Text>
            <Text style={{ color: 'white', fontSize: 13, fontWeight: '500' }}>Add Log</Text>
          </TouchableOpacity>
        </View>

        {/* Legend */}
        <View style={{ flexDirection: 'row', gap: 16, paddingHorizontal: 20, marginBottom: 16 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: '#fca450' }} />
            <Text style={{ fontSize: 12, color: '#888' }}>Food</Text>
          </View>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: '#b2939b' }} />
            <Text style={{ fontSize: 12, color: '#888' }}>Symptom</Text>
          </View>
        </View>

        {/* Content */}
        {loading ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
            <ActivityIndicator size="large" color="#b2939b" />
          </View>
        ) : error ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 }}>
            <Text style={{ color: '#C85A4A', textAlign: 'center', marginBottom: 16 }}>{error}</Text>
            <TouchableOpacity
              onPress={() => { setLoading(true); load().finally(() => setLoading(false)); }}
              style={{
                backgroundColor: '#B8624F',
                paddingHorizontal: 24,
                paddingVertical: 10,
                borderRadius: 20,
              }}
            >
              <Text style={{ color: 'white', fontWeight: '600' }}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : entries.length === 0 ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 }}>
            <Text style={{ fontSize: 48, marginBottom: 12 }}>📋</Text>
            <Text style={{ fontSize: 18, color: '#b2939b', fontWeight: '600', textAlign: 'center' }}>
              No logs yet
            </Text>
            <Text style={{ fontSize: 14, color: '#aaa', textAlign: 'center', marginTop: 8 }}>
              Tap + Add Log to record your first food or symptom entry.
            </Text>
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 40 }}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#b2939b" />
            }
          >
            {groups.map((group) => (
              <View key={group.dateKey}>
                {/* Date header */}
                <View
                  style={{
                    flexDirection: 'row',
                    alignItems: 'center',
                    marginBottom: 12,
                    marginTop: 8,
                  }}
                >
                  <Text style={{ fontSize: 14, fontWeight: '700', color: '#7B5B6B', marginRight: 8 }}>
                    {group.label}
                  </Text>
                  <View style={{ flex: 1, height: 1, backgroundColor: '#DDD' }} />
                  <Text style={{ fontSize: 12, color: '#aaa', marginLeft: 8 }}>
                    {group.items.length} {group.items.length === 1 ? 'entry' : 'entries'}
                  </Text>
                </View>

                {/* Entries */}
                {group.items.map((entry) =>
                  entry.type === 'food' ? (
                    <FoodCard key={entry.id} entry={entry} />
                  ) : (
                    <SymptomCard key={entry.id} entry={entry} />
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
