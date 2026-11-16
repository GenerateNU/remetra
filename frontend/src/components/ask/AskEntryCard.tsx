import { Pressable, Text, View } from 'react-native';
import { CaretRightIcon, SparkleEntryIcon } from './icons';
import { useAskFonts } from './useAskFonts';

/** Figma "Ask / Entry card": opens Ask Remetra from another tab. */
export function AskEntryCard({
  title,
  subtitle,
  onPress,
}: {
  title: string;
  subtitle: string;
  onPress: () => void;
}) {
  useAskFonts();
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${title}. ${subtitle}`}
      onPress={onPress}
      className="w-full flex-row items-center gap-3 rounded-[24px] border border-remetra-line-subtle bg-white p-4"
      style={({ pressed }) => ({ opacity: pressed ? 0.8 : 1 })}
    >
      <View className="rounded-full bg-remetra-canvas p-3">
        <SparkleEntryIcon width={20} height={20} />
      </View>
      <View className="flex-1 gap-0.5">
        <Text className="font-figtree-semibold text-[14px] leading-5 text-remetra-text-primary">{title}</Text>
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">{subtitle}</Text>
      </View>
      <CaretRightIcon width={16} height={16} />
    </Pressable>
  );
}
