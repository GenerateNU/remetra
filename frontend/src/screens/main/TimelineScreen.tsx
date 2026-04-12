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

/** Maps a 1–10 intensity level to a full Tailwind bg class. */
function intensityBgCls(level: number) {
  if (level >= 7) return 'bg-remetra-rose';
  if (level >= 4) return 'bg-remetra-coral';
  return 'bg-remetra-mauve';
}

/** Maps a 1–10 intensity level to its hex value (needed for borderLeftColor). */
function intensityHex(level: number) {
  if (level >= 7) return '#C85A4A'; /* remetra-rose */
  if (level >= 4) return '#D9806E'; /* remetra-coral */
  return '#b2939b';                 /* remetra-mauve */
}

// ─── shared edit helpers ──────────────────────────────────────────────────────

function EditLabel({ children }: { children: string }) {
  return (
    <Text className="text-xs font-semibold text-neutral-500 mb-1 mt-2.5 tracking-wide">
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
    onChange(integerOnly ? v.replace(/[^0-9]/g, '') : v);
  };

  return (
    <TextInput
      value={value}
      onChangeText={handleChange}
      placeholder={placeholder}
      placeholderTextColor="#bbb"
      multiline={multiline}
      keyboardType={integerOnly ? 'number-pad' : 'default'}
      className="border border-[#E0D0D8] rounded-lg px-2.5 py-2 text-sm text-neutral-700 bg-white"
      style={{
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
    <View className="flex-row gap-2 mt-3.5">
      <TouchableOpacity
        onPress={onCancel}
        className="flex-1 py-2.5 rounded-lg border border-remetra-border items-center"
      >
        <Text className="text-sm text-remetra-muted">Cancel</Text>
      </TouchableOpacity>
      <TouchableOpacity
        onPress={onSave}
        disabled={saving}
        className="flex-[2] py-2.5 rounded-lg bg-remetra-burgundy items-center"
        style={{ opacity: saving ? 0.6 : 1 }}
      >
        {saving ? (
          <ActivityIndicator size="small" color="white" />
        ) : (
          <Text className="text-sm text-white font-semibold">Save Changes</Text>
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
      className="rounded-xl mb-2.5 overflow-hidden"
      style={{ backgroundColor: '#FEF0E7', borderLeftWidth: 4, borderLeftColor: '#fca450' /* remetra-orange */ }}
    >
      <TouchableOpacity
        onPress={() => setExpanded((prev) => !prev)}
        activeOpacity={0.7}
        className="p-3.5"
      >
        <View className="flex-row justify-between items-start">
          <View className="flex-1">
            <View className="flex-row items-center gap-1.5 mb-1">
              <Text className="text-base">🍽</Text>
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
          <View className="items-end gap-1 ml-2">
            <Text style={{ fontSize: 12, color: '#B07850' }}>{formatTime(entry.timestamp)}</Text>
            <Text style={{ fontSize: 11, color: '#B07850' }}>{expanded ? '▲ collapse' : '▼ edit'}</Text>
          </View>
        </View>
      </TouchableOpacity>

      {expanded && (
        <View className="px-3.5 pb-3.5" style={{ borderTopWidth: 1, borderTopColor: '#FAD9C4' }}>
          <EditLabel>Quantity</EditLabel>
          <EditTextInput value={quantity} onChange={setQuantity} placeholder="e.g. 2" integerOnly />

          <EditLabel>Date & Time</EditLabel>
          <LogDateTimePicker value={timestamp} onChange={setTimestamp} />

          <EditLabel>Notes</EditLabel>
          <EditTextInput value={notes} onChange={setNotes} placeholder="Optional notes…" multiline />

          {error ? (
            <Text className="text-remetra-rose text-xs mt-2">{error}</Text>
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

  const intHex = intensityHex(intensity);
  const intBgCls = intensityBgCls(intensity);

  return (
    <View
      className="rounded-xl mb-2.5 overflow-hidden"
      style={{ backgroundColor: '#FBF0F2', borderLeftWidth: 4, borderLeftColor: intHex }}
    >
      <TouchableOpacity
        onPress={() => setExpanded((prev) => !prev)}
        activeOpacity={0.7}
        className="p-3.5"
      >
        <View className="flex-row justify-between items-start">
          <View className="flex-1">
            <View className="flex-row items-center gap-1.5 mb-1">
              <Text className="text-base">🩺</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#7B3B4E' }}>{entry.name}</Text>
            </View>
            <View className="flex-row items-center gap-2 mb-0.5">
              <View className={`${intBgCls} rounded-[10px] px-2 py-0.5`}>
                <Text className="text-white text-xs font-semibold">
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
          <View className="items-end gap-1 ml-2">
            <Text style={{ fontSize: 12, color: '#9E7080' }}>{formatTime(entry.timestamp)}</Text>
            <Text style={{ fontSize: 11, color: '#9E7080' }}>{expanded ? '▲ collapse' : '▼ edit'}</Text>
          </View>
        </View>
      </TouchableOpacity>

      {expanded && (
        <View className="px-3.5 pb-3.5" style={{ borderTopWidth: 1, borderTopColor: '#F0D0DA' }}>
          <EditLabel>Intensity</EditLabel>
          <View className="flex-row flex-wrap gap-1.5">
            {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
              <TouchableOpacity
                key={n}
                onPress={() => setIntensity(n)}
                className={`w-9 h-9 rounded-[18px] justify-center items-center ${
                  intensity === n ? intensityBgCls(n) : 'bg-[#F5E8EC]'
                }`}
                style={{
                  borderWidth: intensity === n ? 0 : 1,
                  borderColor: '#E0C8D0',
                }}
              >
                <Text
                  className={`text-[13px] font-semibold ${intensity === n ? 'text-white' : 'text-[#9E7080]'}`}
                >
                  {n}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <EditLabel>Date & Time</EditLabel>
          <LogDateTimePicker value={timestamp} onChange={setTimestamp} />

          <View className="flex-row items-center gap-2 mt-2.5">
            <TouchableOpacity
              onPress={() => setHasDuration((prev) => !prev)}
              className={`w-5 h-5 rounded border justify-center items-center ${
                hasDuration ? 'bg-remetra-burgundy border-remetra-burgundy' : 'bg-white border-remetra-border'
              }`}
            >
              {hasDuration ? <Text className="text-white text-xs">✓</Text> : null}
            </TouchableOpacity>
            <Text style={{ fontSize: 13, color: '#7B3B4E' }}>Duration (minutes)</Text>
          </View>
          {hasDuration && (
            <View className="mt-1.5">
              <EditTextInput value={duration} onChange={setDuration} placeholder="e.g. 30" integerOnly />
            </View>
          )}

          <EditLabel>Notes</EditLabel>
          <EditTextInput value={notes} onChange={setNotes} placeholder="Optional notes…" multiline />

          {error ? (
            <Text className="text-remetra-rose text-xs mt-2">{error}</Text>
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
