import { Pressable, Text, View } from 'react-native';
import { CardShell, ErrorNote, Eyebrow, FieldRow, FieldValue, SavedBanner } from './CardParts';
import { formatClockTime } from '../../../utils/time';
import type { ChatCard } from '../../../types/chat';

const MAX_INTENSITY = 10;

function IntensityBars({ value }: { value: number }) {
  return (
    <View className="flex-row gap-0.5">
      {Array.from({ length: MAX_INTENSITY }, (_, index) => (
        <View
          key={index}
          className={`h-2.5 w-1.5 rounded-sm ${index < value ? 'bg-remetra-primary' : 'bg-remetra-intensity-off'}`}
        />
      ))}
    </View>
  );
}

/** Figma "Ask / Symptom entry" (screen 07). Saved automatically once the user gives a start time. */
export function SymptomEntryCard({
  card,
  onRetry,
}: {
  card: Extract<ChatCard, { type: 'symptom_entry' }>;
  onRetry: () => void;
}) {
  return (
    <CardShell strongBorder>
      <Eyebrow>Symptom entry</Eyebrow>
      <FieldRow first label="Feeling">
        <FieldValue>{card.feeling}</FieldValue>
      </FieldRow>
      <FieldRow first={false} label="Where">
        <FieldValue>{card.where}</FieldValue>
      </FieldRow>
      <View
        accessible
        accessibilityLabel={`How strong: ${card.intensity} of ${MAX_INTENSITY}`}
        className="flex-row items-center border-t border-remetra-line-subtle pt-[7px]"
      >
        <Text className="font-figtree text-[13px] text-remetra-text-tertiary">How strong</Text>
        <IntensityBars value={card.intensity} />
        <FieldValue>{`${card.intensity} of ${MAX_INTENSITY}`}</FieldValue>
      </View>
      <FieldRow first={false} label="Started">
        <FieldValue>{formatClockTime(card.startedAt)}</FieldValue>
      </FieldRow>
      {card.status === 'saved' && <SavedBanner text="Saved to today’s log" />}
      {card.status === 'saving' && (
        <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">Saving…</Text>
      )}
      {card.status === 'error' && (
        <Pressable accessibilityRole="button" onPress={onRetry}>
          <ErrorNote>Couldn’t save that entry. Tap to try again.</ErrorNote>
        </Pressable>
      )}
    </CardShell>
  );
}
