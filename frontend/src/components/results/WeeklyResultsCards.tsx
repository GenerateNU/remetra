import { Text, View } from 'react-native';
import { CircleCheck, Hourglass, Sparkles } from 'lucide-react-native';
import type { WeeklyLabelItem } from '../../types/weeklyResults';

/**
 * Cards for the weekly results screen. Styling follows InsightCard / CardParts on PR #174
 * (Figma "Ask / Insight card"). These only ever show labels, never confidence numbers.
 */

const TRIGGER_TEXT = '#78350f';
const FINE_TEXT = '#065f46';
const LEARNING_TEXT = '#7a7068';

const GROUP_NOTE = 'Always eaten together, so they are checked as one';

function Pill({ label, tone }: { label: string; tone: 'trigger' | 'fine' | 'learning' }) {
  const styles = {
    trigger: { text: 'text-remetra-trigger-text', color: TRIGGER_TEXT, Icon: Sparkles },
    fine: { text: 'text-remetra-fine-text', color: FINE_TEXT, Icon: CircleCheck },
    learning: { text: 'text-remetra-text-tertiary', color: LEARNING_TEXT, Icon: Hourglass },
  }[tone];
  const { Icon } = styles;
  return (
    <View className="flex-row items-center gap-1.5 self-start rounded-full bg-white px-3 py-1">
      <Icon size={13} color={styles.color} strokeWidth={2} />
      <Text className={`font-figtree-semibold text-[12px] leading-4 tracking-[0.12px] ${styles.text}`}>{label}</Text>
    </View>
  );
}

/** One amber card per likely trigger, matching InsightCard. */
export function LikelyTriggerCard({ item }: { item: WeeklyLabelItem }) {
  return (
    <View
      testID={`likely-trigger-${item.id}`}
      className="w-full gap-3 rounded-[24px] border border-remetra-trigger-line bg-remetra-trigger-bg p-5"
    >
      <Pill label="Likely trigger" tone="trigger" />
      <Text className="font-prata text-[20px] leading-7 text-remetra-text-primary">{item.display_name}</Text>
      <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
        Your symptoms kept following meals with this. Try a break from it and see if you feel better.
      </Text>
      {item.is_group ? (
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">{GROUP_NOTE}</Text>
      ) : null}
    </View>
  );
}

function FoodRow({ item, first }: { item: WeeklyLabelItem; first: boolean }) {
  return (
    <View testID={`food-row-${item.id}`} className={first ? '' : 'border-t border-remetra-line-subtle pt-2.5'}>
      <Text className="font-figtree-semibold text-[15px] leading-5 text-remetra-text-primary">{item.display_name}</Text>
      {item.is_group ? (
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">{GROUP_NOTE}</Text>
      ) : null}
    </View>
  );
}

const LIST_COPY = {
  looks_fine: {
    pill: 'Looks fine',
    tone: 'fine' as const,
    body: 'You have eaten these a few times without a pattern of symptoms.',
    card: 'border-remetra-fine-line/30 bg-remetra-fine-bg',
  },
  still_learning: {
    pill: 'Still learning',
    tone: 'learning' as const,
    body: 'Not enough yet to say either way. Keep eating as usual and logging.',
    card: 'border-remetra-chip-line bg-white',
  },
};

/** A card listing every food under one label: looks fine or still learning. */
export function LabelListCard({ label, items }: { label: 'looks_fine' | 'still_learning'; items: WeeklyLabelItem[] }) {
  if (items.length === 0) return null;
  const copy = LIST_COPY[label];
  return (
    <View testID={`label-list-${label}`} className={`w-full gap-3 rounded-[20px] border px-4 py-4 ${copy.card}`}>
      <Pill label={copy.pill} tone={copy.tone} />
      <Text className="font-figtree text-[13px] leading-5 text-remetra-text-secondary">{copy.body}</Text>
      <View className="gap-2.5">
        {items.map((item, index) => (
          <FoodRow key={item.id} item={item} first={index === 0} />
        ))}
      </View>
    </View>
  );
}

/** Shown when most foods look fine and nothing stands out. */
export function NoClearPatternCard() {
  return (
    <View
      testID="no-clear-pattern"
      className="w-full gap-2 rounded-[24px] border border-remetra-fine-line/30 bg-remetra-fine-bg p-5"
    >
      <Pill label="No clear food pattern" tone="fine" />
      <Text className="font-prata text-[20px] leading-7 text-remetra-text-primary">Nothing stands out</Text>
      <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
        Most of what you eat looks fine, and no food keeps lining up with your symptoms. Your symptoms may have
        another cause, like sleep, stress or your cycle.
      </Text>
    </View>
  );
}

/** Shown before any food has been eaten often enough to label. */
export function StillLearningEmptyCard() {
  return (
    <View testID="still-learning-empty" className="w-full gap-2 rounded-[24px] border border-remetra-chip-line bg-white p-5">
      <Pill label="Still learning" tone="learning" />
      <Text className="font-prata text-[20px] leading-7 text-remetra-text-primary">Your first results are on the way</Text>
      <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
        Keep logging your meals and symptoms. Foods show up here once you have eaten them a few times.
      </Text>
    </View>
  );
}
