import React from 'react';
import { ActivityIndicator, Text, TextInput, TouchableOpacity, View } from 'react-native';

// ─── time formatting ──────────────────────────────────────────────────────────

export function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ─── intensity helpers ────────────────────────────────────────────────────────

/** Maps a 1–10 intensity level to a full Tailwind bg class. */
export function intensityBgCls(level: number) {
  if (level >= 7) return 'bg-remetra-rose';
  if (level >= 4) return 'bg-remetra-coral';
  return 'bg-remetra-mauve';
}

/** Maps a 1–10 intensity level to its hex value (needed for borderLeftColor). */
export function intensityHex(level: number) {
  if (level >= 7) return '#C85A4A'; /* remetra-rose */
  if (level >= 4) return '#D9806E'; /* remetra-coral */
  return '#b2939b';                 /* remetra-mauve */
}

// ─── shared edit UI components ────────────────────────────────────────────────

export function EditLabel({ children }: { children: string }) {
  return (
    <Text className="text-xs font-semibold text-neutral-500 mb-1 mt-2.5 tracking-wide">
      {children.toUpperCase()}
    </Text>
  );
}

export function EditTextInput({
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

export function SaveCancelRow({
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
