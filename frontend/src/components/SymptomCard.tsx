import React, { useState } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import { symptomLogService } from '../api/symptom_log_service';
import { LogDateTimePicker } from './LogDateTimePicker';
import { SymptomTimelineEntry } from '../types/timeline';
import {
  EditLabel,
  EditTextInput,
  SaveCancelRow,
  formatTime,
  intensityBgCls,
  intensityHex,
} from './TimelineCardHelpers';

export function SymptomCard({
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
