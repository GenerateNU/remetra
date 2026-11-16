import { Linking, Pressable, Text, View } from 'react-native';
import { CardTitle, Eyebrow } from './CardParts';
import { ClockStarterIcon, SparkleTagIcon, WarningIcon } from '../icons';
import type { ChatCard } from '../../../types/chat';

/** Figma "Ask / Next update" (screen 10a: too early to tell). */
export function NextUpdateCard({ card }: { card: Extract<ChatCard, { type: 'next_update' }> }) {
  return (
    <View className="h-[100px] flex-row items-center gap-2.5 self-start rounded-2xl border border-remetra-line-subtle bg-white px-3 py-2.5">
      <View className="h-8 w-8 items-center justify-center rounded-full bg-remetra-canvas">
        <ClockStarterIcon width={16} height={16} />
      </View>
      <View>
        <Text className="font-figtree text-[12px] text-remetra-text-tertiary">{card.label}</Text>
        <Text className="font-figtree-semibold text-[14px] text-remetra-text-primary">{card.when}</Text>
      </View>
    </View>
  );
}

/** Figma "Ask / Likely trigger tag" (screen 10b: no numbers, just the bucket). */
export function LikelyTriggerTag() {
  return (
    <View className="flex-row items-center gap-1.5 self-start rounded-full border border-remetra-trigger-line bg-remetra-trigger-bg px-2.5 py-1">
      <SparkleTagIcon width={13} height={13} />
      <Text className="font-figtree-semibold text-[12px] text-remetra-trigger-text">Likely trigger</Text>
    </View>
  );
}

/** Figma "Ask / Safety banner" (screen 11). */
export function SafetyBanner({ card }: { card: Extract<ChatCard, { type: 'safety' }> }) {
  return (
    <View accessibilityRole="alert" className="w-full gap-4 rounded-[24px] bg-remetra-emergency p-5">
      <View className="flex-row gap-3">
        <WarningIcon width={24} height={24} />
        <View className="flex-1 gap-1">
          <Text className="font-figtree-semibold text-[16px] leading-6 text-white">{card.title}</Text>
          <Text className="font-figtree text-[14px] leading-5 text-white">{card.body}</Text>
        </View>
      </View>
      <Pressable
        accessibilityRole="button"
        onPress={() => void Linking.openURL(`tel:${card.phoneNumber}`)}
        className="w-full items-center justify-center rounded-full border-2 border-remetra-chip-strong bg-white px-6 py-4"
        style={({ pressed }) => ({ opacity: pressed ? 0.88 : 1 })}
      >
        <Text className="font-figtree-semibold text-[16px] leading-5 tracking-[0.16px] text-remetra-emergency-label">
          {card.actionLabel}
        </Text>
      </Pressable>
    </View>
  );
}

const BUCKET_TAGS = [
  { key: 'likelyTrigger', label: 'Likely trigger', className: 'border-remetra-trigger-line bg-remetra-trigger-bg', text: 'text-remetra-trigger-text' },
  { key: 'looksFine', label: 'Looks fine', className: 'border-remetra-fine-line bg-remetra-fine-bg', text: 'text-remetra-fine-text' },
  { key: 'stillLearning', label: 'Still learning', className: 'border-remetra-chip-line bg-remetra-line-subtle', text: 'text-remetra-text-secondary' },
] as const;

/** Figma "Ask / Weekly update" (screen 12: proactive Sunday message). */
export function WeeklyUpdateCard({ card }: { card: Extract<ChatCard, { type: 'weekly_update' }> }) {
  return (
    <View className="w-full gap-3 rounded-[20px] border border-remetra-line-subtle bg-white px-4 py-3.5">
      <Eyebrow>{card.eyebrow}</Eyebrow>
      <CardTitle>{card.title}</CardTitle>
      <View className="flex-row flex-wrap gap-1.5">
        {BUCKET_TAGS.map((tag) => (
          <View key={tag.key} className={`rounded-full border px-2.5 py-1 ${tag.className}`}>
            <Text className={`font-figtree-semibold text-[12px] ${tag.text}`}>
              {tag.label} · {card.counts[tag.key]}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}
