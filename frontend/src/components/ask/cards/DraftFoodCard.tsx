import { Text, View } from 'react-native';
import { ButtonRow, CardShell, ErrorNote, Eyebrow, FieldRow, FieldValue } from './CardParts';
import { PillButton } from '../PillButton';
import { formatClockTime } from '../../../utils/time';
import type { ChatCard } from '../../../types/chat';

/** Figma "Ask / Draft entry" (screen 06). Becomes a SavedBanner once saved. */
export function DraftFoodCard({
  card,
  onSave,
  onEdit,
}: {
  card: Extract<ChatCard, { type: 'draft_food' }>;
  onSave: () => void;
  onEdit: () => void;
}) {
  const saving = card.status === 'saving';
  return (
    <CardShell strongBorder>
      <View className="flex-row items-center justify-between">
        <Eyebrow>Draft food entry</Eyebrow>
        <View className="rounded-full bg-remetra-line-subtle px-2.5 py-1">
          <Text className="font-figtree-semibold text-[12px] text-remetra-text-secondary">Not saved yet</Text>
        </View>
      </View>
      <FieldRow first label="Food">
        <FieldValue>{card.food}</FieldValue>
      </FieldRow>
      <FieldRow first={false} label="Meal">
        <FieldValue>{card.meal}</FieldValue>
      </FieldRow>
      <FieldRow first={false} label="Time">
        <FieldValue>{formatClockTime(card.loggedAt)}</FieldValue>
      </FieldRow>
      {card.status === 'error' && <ErrorNote>Couldn’t save that entry. Please try again.</ErrorNote>}
      <ButtonRow>
        <PillButton label={saving ? 'Saving…' : 'Save to log'} onPress={onSave} disabled={saving} fill />
        <PillButton label="Edit" onPress={onEdit} variant="ghost" disabled={saving} fill />
      </ButtonRow>
    </CardShell>
  );
}
