import { Pressable, Text, View } from 'react-native';
import CaretRightLink from '../../assets/insights/caret-right-link.svg';
import { BloomRing } from './BloomRing';

/** Figma "Progress card" (insights unlocked): how many food groups have a result, and when the next update is. */
export function ProgressCard({
  checked,
  total,
  nextUpdate,
  onSeeInsights,
}: {
  checked: number;
  total: number;
  nextUpdate: string;
  onSeeInsights: () => void;
}) {
  return (
    <View
      testID="progress-card"
      className="w-full flex-row items-center gap-4 rounded-[24px] border-[0.5px] border-remetra-line-subtle bg-white p-5"
      style={{
        shadowColor: '#63311f',
        shadowOpacity: 0.08,
        shadowRadius: 6,
        shadowOffset: { width: 0, height: 8 },
        elevation: 3,
      }}
    >
      <BloomRing progress={total > 0 ? checked / total : 0} />
      <View className="flex-1 gap-1">
        <Text className="font-figtree-semibold text-[16px] leading-6 text-remetra-text-primary">
          {`We’ve checked ${checked} of ${total} food groups`}
        </Text>
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-secondary">{`Next update ${nextUpdate}`}</Text>
        <Pressable
          onPress={onSeeInsights}
          accessibilityRole="button"
          className="flex-row items-center gap-0.5 self-start py-1"
          style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}
        >
          <Text className="font-figtree-semibold text-[14px] leading-5 tracking-[0.14px] text-remetra-text-primary">
            See insights
          </Text>
          <CaretRightLink width={14} height={14} />
        </Pressable>
      </View>
    </View>
  );
}
