import { Pressable, Text, View } from 'react-native';
import SparkleEntry from '../../assets/insights/sparkle-entry.svg';
import CaretRightEntry from '../../assets/insights/caret-right-entry.svg';

/**
 * Figma "Ask entry": opens Ask Remetra. The chat screen lives on the chatbot PR (#174), so until it merges the
 * card renders without a press action.
 * TODO: pass onPress={() => navigation.navigate('AskRemetra', { entry: 'insights' })} once #174 is merged.
 */
export function AskEntryCard({ onPress }: { onPress?: () => void }) {
  return (
    <Pressable
      testID="ask-entry-card"
      onPress={onPress}
      disabled={!onPress}
      accessibilityRole={onPress ? 'button' : undefined}
      className="w-full flex-row items-center gap-3 rounded-[24px] border-[0.5px] border-remetra-line-subtle bg-white p-4"
    >
      <View className="rounded-full bg-remetra-line-subtle p-3">
        <SparkleEntry width={20} height={20} />
      </View>
      <View className="flex-1 gap-0.5">
        <Text className="font-figtree-semibold text-[14px] leading-5 text-remetra-text-primary">Ask about your results</Text>
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
          Get answers from your own logs and labs
        </Text>
      </View>
      <CaretRightEntry width={16} height={16} />
    </Pressable>
  );
}
