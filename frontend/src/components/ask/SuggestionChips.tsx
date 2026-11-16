import { Pressable, Text, View } from 'react-native';

export function SuggestionChips({
  items,
  onSelect,
  disabled = false,
}: {
  items: string[];
  onSelect: (item: string) => void;
  disabled?: boolean;
}) {
  return (
    <View className="flex-row flex-wrap gap-1.5">
      {items.map((item) => (
        <Pressable
          key={item}
          accessibilityRole="button"
          disabled={disabled}
          onPress={() => onSelect(item)}
          className="items-center justify-center rounded-full border border-remetra-chip-line bg-white px-4 py-2"
          style={({ pressed }) => ({ opacity: pressed ? 0.7 : 1 })}
        >
          <Text className="font-figtree text-[14px] leading-5 text-remetra-text-primary">{item}</Text>
        </Pressable>
      ))}
    </View>
  );
}
