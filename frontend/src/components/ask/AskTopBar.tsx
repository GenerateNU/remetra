import { Pressable, Text, View } from 'react-native';
import { CaretLeftIcon } from './icons';

export function AskTopBar({ title, onBack }: { title: string; onBack: () => void }) {
  return (
    <View className="flex-row items-center gap-2 px-4 py-3">
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Back"
        onPress={onBack}
        hitSlop={8}
        className="rounded-full border border-remetra-line-subtle bg-white p-2"
        style={({ pressed }) => ({ opacity: pressed ? 0.7 : 1 })}
      >
        <CaretLeftIcon width={20} height={20} />
      </Pressable>
      <Text
        accessibilityRole="header"
        className="flex-1 text-center font-figtree-semibold text-[16px] leading-6 text-remetra-text-primary"
      >
        {title}
      </Text>
      <View className="h-9 w-9" />
    </View>
  );
}
