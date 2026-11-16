import { Text, View } from 'react-native';
import { SparkleInsightIcon } from '../icons';
import type { ChatCard } from '../../../types/chat';

/** Figma "Ask / Insight card · likely trigger". */
export function InsightCard({ card }: { card: Extract<ChatCard, { type: 'insight' }> }) {
  return (
    <View className="w-full gap-3 rounded-[24px] border border-remetra-trigger-line bg-remetra-trigger-bg p-5">
      <View className="flex-row items-center gap-2 self-start rounded-full bg-white px-3 py-1">
        <SparkleInsightIcon width={14} height={14} />
        <Text className="font-figtree-semibold text-[12px] leading-4 tracking-[0.12px] text-remetra-trigger-text">
          Likely trigger
        </Text>
      </View>
      <Text className="font-prata text-[20px] leading-7 text-remetra-text-primary">{card.title}</Text>
      <View>
        {card.evidence.map((line) => (
          <Text key={line} className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
            {line}
          </Text>
        ))}
      </View>
    </View>
  );
}
