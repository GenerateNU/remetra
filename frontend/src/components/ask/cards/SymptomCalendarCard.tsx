import { Text, View } from 'react-native';
import { CardShell, Eyebrow } from './CardParts';
import type { ChatCard, DayStatus } from '../../../types/chat';

const DAY_LETTERS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

const CELL_CLASS: Record<DayStatus, string> = {
  symptoms: 'bg-remetra-day-symptoms',
  clear: 'bg-remetra-day-clear',
  not_logged: 'border border-dashed border-remetra-day-unlogged-line bg-remetra-day-unlogged',
};

const LEGEND: { status: DayStatus; label: string }[] = [
  { status: 'symptoms', label: 'Symptoms' },
  { status: 'clear', label: 'No symptoms' },
  { status: 'not_logged', label: 'Not logged' },
];

const STATUS_LABEL: Record<DayStatus, string> = {
  symptoms: 'symptoms',
  clear: 'no symptoms',
  not_logged: 'not logged',
};

/** Figma "Ask / Symptom calendar". */
export function SymptomCalendarCard({ card }: { card: Extract<ChatCard, { type: 'symptom_calendar' }> }) {
  return (
    <CardShell>
      <Eyebrow>{card.title}</Eyebrow>
      <View className="gap-[5px]">
        <View className="flex-row items-center gap-[5px]">
          <View className="w-[46px]" />
          {DAY_LETTERS.map((letter, index) => (
            <Text
              key={`${letter}-${index}`}
              className="w-[26px] text-center font-figtree text-[11px] text-remetra-text-tertiary"
            >
              {letter}
            </Text>
          ))}
        </View>
        {card.weeks.map((week, weekIndex) => (
          <View
            key={weekIndex}
            accessible
            accessibilityLabel={`Week ${weekIndex + 1}: ${week.map((day) => STATUS_LABEL[day]).join(', ')}`}
            className="flex-row items-center gap-[5px]"
          >
            <Text className="w-[46px] font-figtree-semibold text-[11px] text-remetra-text-secondary">
              Week {weekIndex + 1}
            </Text>
            {week.map((day, dayIndex) => (
              <View key={dayIndex} className={`h-5 w-[26px] rounded-md ${CELL_CLASS[day]}`} />
            ))}
          </View>
        ))}
      </View>
      <View className="flex-row flex-wrap items-center gap-3">
        {LEGEND.map(({ status, label }) => (
          <View key={status} className="flex-row items-center gap-1.5">
            <View className={`h-2.5 w-2.5 rounded-[3px] ${CELL_CLASS[status]}`} />
            <Text className="font-figtree text-[11px] text-remetra-text-secondary">{label}</Text>
          </View>
        ))}
      </View>
    </CardShell>
  );
}
