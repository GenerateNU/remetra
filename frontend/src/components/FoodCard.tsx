import React, { useState } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import { foodLogService } from '../api/food_log_service';
import { LogDateTimePicker } from './LogDateTimePicker';
import { FoodTimelineEntry } from '../types/timeline';
import { EditLabel, EditTextInput, SaveCancelRow, formatTime } from './TimelineCardHelpers';

export function FoodCard({
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
