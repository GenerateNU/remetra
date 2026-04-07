import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { LogDateTimePicker } from '../../components/LogDateTimePicker';
import { foodLogService, FoodLogResponse } from '../../api/food_log_service';
import { symptomLogService, SymptomLogResponse } from '../../api/symptom_log_service';
import { useBankStore } from '../../store/bankStore';
import { useUIStore } from '../../store/uiStore';

// ─── unified entry ────────────────────────────────────────────────────────────

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

// ─── helpers ──────────────────────────────────────────────────────────────────

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
    if (!map.has(key)) map.set(key, { label: formatDateHeader(d), items: [] });
    map.get(key)!.items.push(entry);
  }
  return Array.from(map.entries()).map(([dateKey, val]) => ({ dateKey, ...val }));
}

// ─── shared edit row helpers ──────────────────────────────────────────────────

function EditLabel({ children }: { children: string }) {
  return (
    <Text style={{ fontSize: 12, fontWeight: '600', color: '#888', marginBottom: 4, marginTop: 10 }}>
      {children.toUpperCase()}
    </Text>
  );
}

function EditTextInput({
  value,
  onChange,
  placeholder,
  multiline,
  integerOnly,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  multiline?: boolean;
  integerOnly?: boolean;
}) {
  const handleChange = (v: string) => {
    if (integerOnly) {
      onChange(v.replace(/[^0-9]/g, ''));
    } else {
      onChange(v);
    }
  };

  return (
    <TextInput
      value={value}
      onChangeText={handleChange}
      placeholder={placeholder}
      placeholderTextColor="#bbb"
      multiline={multiline}
      keyboardType={integerOnly ? 'number-pad' : 'default'}
      style={{
        borderWidth: 1,
        borderColor: '#E0D0D8',
        borderRadius: 8,
        paddingHorizontal: 10,
        paddingVertical: 8,
        fontSize: 14,
        color: '#333',
        backgroundColor: 'white',
        minHeight: multiline ? 60 : undefined,
        textAlignVertical: multiline ? 'top' : undefined,
      }}
    />
  );
}

function SaveCancelRow({
  saving,
  onSave,
  onCancel,
}: {
  saving: boolean;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <View style={{ flexDirection: 'row', gap: 8, marginTop: 14 }}>
      <TouchableOpacity
        onPress={onCancel}
        style={{
          flex: 1,
          paddingVertical: 10,
          borderRadius: 8,
          borderWidth: 1,
          borderColor: '#ccc',
          alignItems: 'center',
        }}
      >
        <Text style={{ fontSize: 14, color: '#888' }}>Cancel</Text>
      </TouchableOpacity>
      <TouchableOpacity
        onPress={onSave}
        disabled={saving}
        style={{
          flex: 2,
          paddingVertical: 10,
          borderRadius: 8,
          backgroundColor: '#B8624F',
          alignItems: 'center',
          opacity: saving ? 0.6 : 1,
        }}
      >
        {saving ? (
          <ActivityIndicator size="small" color="white" />
        ) : (
          <Text style={{ fontSize: 14, color: 'white', fontWeight: '600' }}>Save Changes</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

// ─── food card ────────────────────────────────────────────────────────────────

function FoodCard({
  entry,
  onUpdate,
}: {
  entry: FoodTimelineEntry;
  onUpdate: (updated: Partial<FoodTimelineEntry>) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [quantity, setQuantity] = useState(entry.quantity ?? '');
  const [notes, setNotes] = useState(entry.notes ?? '');
  const [timestamp, setTimestamp] = useState(entry.timestamp);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCancel = () => {
    setQuantity(entry.quantity ?? '');
    setNotes(entry.notes ?? '');
    setTimestamp(entry.timestamp);
    setError(null);
    setExpanded(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await foodLogService.updateFoodLog(entry.id, {
        quantity: quantity || undefined,
        notes: notes || undefined,
        timestamp: timestamp.toISOString(),
      });
      onUpdate({ quantity: quantity || null, notes: notes || null, timestamp });
      setExpanded(false);
    } catch {
      setError('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <View
      style={{
        backgroundColor: '#FEF0E7',
        borderLeftWidth: 4,
        borderLeftColor: '#fca450',
        borderRadius: 12,
        marginBottom: 10,
        overflow: 'hidden',
      }}
    >
      {/* Collapsed header — always visible */}
      <TouchableOpacity
        onPress={() => setExpanded((prev) => !prev)}
        activeOpacity={0.7}
        style={{ padding: 14 }}
      >
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              <Text style={{ fontSize: 16 }}>🍽</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#7C4A1E' }}>{entry.name}</Text>
            </View>
            {entry.quantity ? (
              <Text style={{ fontSize: 13, color: '#A0673A', marginBottom: 2 }}>Qty: {entry.quantity}</Text>
            ) : null}
            {entry.ingredients.length > 0 && (
              <Text style={{ fontSize: 12, color: '#B07850' }} numberOfLines={expanded ? undefined : 2}>
                {entry.ingredients.join(', ')}
              </Text>
            )}
            {!expanded && entry.notes ? (
              <Text style={{ fontSize: 12, color: '#9E7050', marginTop: 4, fontStyle: 'italic' }} numberOfLines={1}>
                {entry.notes}
              </Text>
            ) : null}
          </View>
          <View style={{ alignItems: 'flex-end', gap: 4, marginLeft: 8 }}>
            <Text style={{ fontSize: 12, color: '#B07850' }}>{formatTime(entry.timestamp)}</Text>
            <Text style={{ fontSize: 11, color: '#B07850' }}>{expanded ? '▲ collapse' : '▼ edit'}</Text>
          </View>
        </View>
      </TouchableOpacity>

      {/* Expanded edit form */}
      {expanded && (
        <View style={{ paddingHorizontal: 14, paddingBottom: 14, borderTopWidth: 1, borderTopColor: '#FAD9C4' }}>
          <EditLabel>Quantity</EditLabel>
          <EditTextInput value={quantity} onChange={setQuantity} placeholder="e.g. 2" integerOnly />

          <EditLabel>Date & Time</EditLabel>
          <LogDateTimePicker value={timestamp} onChange={setTimestamp} />

          <EditLabel>Notes</EditLabel>
          <EditTextInput value={notes} onChange={setNotes} placeholder="Optional notes…" multiline />

          {error ? (
            <Text style={{ color: '#C85A4A', fontSize: 12, marginTop: 8 }}>{error}</Text>
          ) : null}

          <SaveCancelRow saving={saving} onSave={handleSave} onCancel={handleCancel} />
        </View>
      )}
    </View>
  );
}

// ─── symptom card ─────────────────────────────────────────────────────────────

function SymptomCard({
  entry,
  onUpdate,
}: {
  entry: SymptomTimelineEntry;
  onUpdate: (updated: Partial<SymptomTimelineEntry>) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [intensity, setIntensity] = useState(entry.intensity);
  const [duration, setDuration] = useState(entry.duration?.toString() ?? '');
  const [hasDuration, setHasDuration] = useState(entry.duration !== null);
  const [notes, setNotes] = useState(entry.notes ?? '');
  const [timestamp, setTimestamp] = useState(entry.timestamp);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const intensityColor = intensity >= 7 ? '#C85A4A' : intensity >= 4 ? '#D9806E' : '#b2939b';

  const handleCancel = () => {
    setIntensity(entry.intensity);
    setDuration(entry.duration?.toString() ?? '');
    setHasDuration(entry.duration !== null);
    setNotes(entry.notes ?? '');
    setTimestamp(entry.timestamp);
    setError(null);
    setExpanded(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const durationVal = hasDuration && duration ? parseInt(duration, 10) : undefined;
      await symptomLogService.updateSymptomLog(entry.id, {
        intensity,
        timestamp: timestamp.toISOString(),
        duration: durationVal,
        notes: notes || undefined,
      });
      onUpdate({
        intensity,
        timestamp,
        duration: durationVal ?? null,
        notes: notes || null,
      });
      setExpanded(false);
    } catch {
      setError('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <View
      style={{
        backgroundColor: '#FBF0F2',
        borderLeftWidth: 4,
        borderLeftColor: intensityColor,
        borderRadius: 12,
        marginBottom: 10,
        overflow: 'hidden',
      }}
    >
      {/* Collapsed header */}
      <TouchableOpacity
        onPress={() => setExpanded((prev) => !prev)}
        activeOpacity={0.7}
        style={{ padding: 14 }}
      >
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              <Text style={{ fontSize: 16 }}>🩺</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#7B3B4E' }}>{entry.name}</Text>
            </View>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 2 }}>
              <View style={{ backgroundColor: intensityColor, borderRadius: 10, paddingHorizontal: 8, paddingVertical: 2 }}>
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
            {!expanded && entry.notes ? (
              <Text style={{ fontSize: 12, color: '#9E7080', marginTop: 4, fontStyle: 'italic' }} numberOfLines={1}>
                {entry.notes}
              </Text>
            ) : null}
          </View>
          <View style={{ alignItems: 'flex-end', gap: 4, marginLeft: 8 }}>
            <Text style={{ fontSize: 12, color: '#9E7080' }}>{formatTime(entry.timestamp)}</Text>
            <Text style={{ fontSize: 11, color: '#9E7080' }}>{expanded ? '▲ collapse' : '▼ edit'}</Text>
          </View>
        </View>
      </TouchableOpacity>

      {/* Expanded edit form */}
      {expanded && (
        <View style={{ paddingHorizontal: 14, paddingBottom: 14, borderTopWidth: 1, borderTopColor: '#F0D0DA' }}>
          <EditLabel>Intensity</EditLabel>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
            {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
              <TouchableOpacity
                key={n}
                onPress={() => setIntensity(n)}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 18,
                  backgroundColor: intensity === n ? intensityColor : '#F5E8EC',
                  justifyContent: 'center',
                  alignItems: 'center',
                  borderWidth: intensity === n ? 0 : 1,
                  borderColor: '#E0C8D0',
                }}
              >
                <Text style={{ fontSize: 13, fontWeight: '600', color: intensity === n ? 'white' : '#9E7080' }}>
                  {n}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <EditLabel>Date & Time</EditLabel>
          <LogDateTimePicker value={timestamp} onChange={setTimestamp} />

          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10 }}>
            <TouchableOpacity
              onPress={() => setHasDuration((prev) => !prev)}
              style={{
                width: 20,
                height: 20,
                borderRadius: 4,
                borderWidth: 1,
                borderColor: '#ccc',
                backgroundColor: hasDuration ? '#B8624F' : 'white',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              {hasDuration ? <Text style={{ color: 'white', fontSize: 12 }}>✓</Text> : null}
            </TouchableOpacity>
            <Text style={{ fontSize: 13, color: '#7B3B4E' }}>Duration (minutes)</Text>
          </View>
          {hasDuration && (
            <View style={{ marginTop: 6 }}>
              <EditTextInput
                value={duration}
                onChange={setDuration}
                placeholder="e.g. 30"
                integerOnly
              />
            </View>
          )}

          <EditLabel>Notes</EditLabel>
          <EditTextInput value={notes} onChange={setNotes} placeholder="Optional notes…" multiline />

          {error ? (
            <Text style={{ color: '#C85A4A', fontSize: 12, marginTop: 8 }}>{error}</Text>
          ) : null}

          <SaveCancelRow saving={saving} onSave={handleSave} onCancel={handleCancel} />
        </View>
      )}
    </View>
  );
}

// ─── main screen ──────────────────────────────────────────────────────────────

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
          <Text style={{ fontSize: 12, color: '#bbb', marginLeft: 4 }}>Tap a card to edit</Text>
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
              style={{ backgroundColor: '#B8624F', paddingHorizontal: 24, paddingVertical: 10, borderRadius: 20 }}
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
            keyboardShouldPersistTaps="handled"
          >
            {groups.map((group) => (
              <View key={group.dateKey}>
                <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12, marginTop: 8 }}>
                  <Text style={{ fontSize: 14, fontWeight: '700', color: '#7B5B6B', marginRight: 8 }}>
                    {group.label}
                  </Text>
                  <View style={{ flex: 1, height: 1, backgroundColor: '#DDD' }} />
                  <Text style={{ fontSize: 12, color: '#aaa', marginLeft: 8 }}>
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
