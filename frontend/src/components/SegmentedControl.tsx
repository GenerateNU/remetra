import { View, Text, TouchableOpacity } from 'react-native';

/** Pill-style single-select toggle, e.g. Sleep / HRV / Resting HR or 7 / 30 / 90 days. */
export function SegmentedControl<T extends string | number>({
  options,
  selected,
  onSelect,
}: {
  options: { value: T; label: string }[];
  selected: T;
  onSelect: (value: T) => void;
}) {
  return (
    <View className="flex-row bg-remetra-surface rounded-full p-1">
      {options.map((o) => {
        const active = o.value === selected;
        return (
          <TouchableOpacity
            key={String(o.value)}
            accessibilityRole="button"
            accessibilityState={{ selected: active }}
            onPress={() => onSelect(o.value)}
            className={`flex-1 items-center rounded-full py-1.5 border ${active ? 'bg-remetra-surface-accent border-remetra-accent' : 'border-transparent'}`}
          >
            <Text className={`text-xs ${active ? 'text-remetra-espresso font-semibold' : 'text-remetra-muted'}`}>
              {o.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}
