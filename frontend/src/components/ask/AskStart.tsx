import { FC } from 'react';
import { Pressable, Text, View } from 'react-native';
import type { SvgProps } from 'react-native-svg';
import { Avatar56, ClockStarterIcon, ForkKnifeIcon, NotebookIcon, SparkleStarterIcon } from './icons';
import { SuggestionChips } from './SuggestionChips';
import { CHAT_USES_MOCK } from '../../api/chat_service';
import { ASK_MARKERS } from '../../store/useChatStore';
import type { ThreadMarker } from '../../types/chat';

interface Starter {
  title: string;
  message: string;
  Icon: FC<SvgProps>;
  marker: ThreadMarker;
}

const MOCK_STARTERS: Starter[] = [
  {
    title: 'Understand my insights',
    message: 'Why is onion & garlic a likely trigger?',
    Icon: SparkleStarterIcon,
    marker: ASK_MARKERS.insights,
  },
  {
    title: 'See change over time',
    message: 'Have my symptoms improved?',
    Icon: ClockStarterIcon,
    marker: ASK_MARKERS.newConversation,
  },
  { title: 'Adapt tonight’s dinner', message: 'I only have 20 minutes', Icon: ForkKnifeIcon, marker: ASK_MARKERS.recipe },
  { title: 'Log by chatting', message: 'I had a turkey sandwich around 1', Icon: NotebookIcon, marker: ASK_MARKERS.log },
];

// POST /chat answers from the user's own logs only: no logging, recipes or general nutrition.
const LIVE_STARTERS: Starter[] = [
  {
    title: 'Understand my insights',
    message: 'What do my logs show about triggers so far?',
    Icon: SparkleStarterIcon,
    marker: ASK_MARKERS.insights,
  },
  {
    title: 'See change over time',
    message: 'Have my symptoms improved?',
    Icon: ClockStarterIcon,
    marker: ASK_MARKERS.newConversation,
  },
  {
    title: 'Look back at meals',
    message: 'How have I felt after meals lately?',
    Icon: ForkKnifeIcon,
    marker: ASK_MARKERS.log,
  },
  {
    title: 'Check my logging',
    message: 'How consistent has my logging been?',
    Icon: NotebookIcon,
    marker: ASK_MARKERS.log,
  },
];

const STARTERS = CHAT_USES_MOCK ? MOCK_STARTERS : LIVE_STARTERS;
const FOLLOW_UPS = CHAT_USES_MOCK ? ['What could I order at a Thai place?'] : ['Which symptom have I logged the most?'];

function StarterCard({ starter, onPress }: { starter: Starter; onPress: () => void }) {
  const { Icon } = starter;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${starter.title}. ${starter.message}`}
      onPress={onPress}
      className="flex-1 gap-2 rounded-[20px] border border-remetra-line-subtle bg-white p-3.5"
      style={({ pressed }) => ({ opacity: pressed ? 0.8 : 1 })}
    >
      <View className="h-8 w-8 items-center justify-center rounded-full bg-remetra-canvas">
        <Icon width={16} height={16} />
      </View>
      <Text className="font-figtree-semibold text-[14px] leading-[19px] text-remetra-text-primary">{starter.title}</Text>
      <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">{starter.message}</Text>
    </Pressable>
  );
}

/** Figma "01 · Ask start": greeting, four starters and a follow-up chip. */
export function AskStart({
  name,
  onSend,
  disabled,
}: {
  name: string | null;
  onSend: (message: string, marker?: ThreadMarker) => void;
  disabled: boolean;
}) {
  const rows = [STARTERS.slice(0, 2), STARTERS.slice(2, 4)];
  return (
    <View className="w-full gap-[18px]">
      <View className="items-center gap-3">
        <Avatar56 width={56} height={56} />
        <Text className="text-center font-prata text-[24px] leading-[30px] text-remetra-text-primary">
          {name ? `Hi ${name}, what would help today?` : 'Hi, what would help today?'}
        </Text>
        <Text className="text-center font-figtree text-[14px] leading-5 text-remetra-text-secondary">
          I answer using your own logs, insights and meal ideas.
        </Text>
      </View>
      <View className="gap-2.5">
        {rows.map((row) => (
          <View key={row[0].title} className="flex-row gap-2.5">
            {row.map((starter) => (
              <StarterCard
                key={starter.title}
                starter={starter}
                onPress={() => !disabled && onSend(starter.message, starter.marker)}
              />
            ))}
          </View>
        ))}
      </View>
      <SuggestionChips items={FOLLOW_UPS} onSelect={(item) => onSend(item)} disabled={disabled} />
    </View>
  );
}
