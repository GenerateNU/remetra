import { Text, View } from 'react-native';
import { ButtonRow, CardShell, CardTitle, ListRow } from './CardParts';
import { ClockTagIcon } from '../icons';
import { PillButton } from '../PillButton';
import type { ChatCard } from '../../../types/chat';

/** Figma "Ask / Recipe adaptation". */
export function RecipeCard({
  card,
  onUse,
  onKeep,
}: {
  card: Extract<ChatCard, { type: 'recipe' }>;
  onUse: () => void;
  onKeep: () => void;
}) {
  return (
    <CardShell>
      <View className="flex-row items-center gap-1.5 self-start rounded-full bg-remetra-canvas px-2.5 py-1">
        <ClockTagIcon width={13} height={13} />
        <Text className="font-figtree-semibold text-[12px] text-remetra-chip-strong">{card.durationLabel}</Text>
      </View>
      <CardTitle>{card.title}</CardTitle>
      <View className="gap-[7px]">
        {card.ingredients.map((ingredient, index) => (
          <ListRow key={ingredient.name} first={index === 0} className="items-start justify-between gap-3">
            <Text className="flex-1 font-figtree text-[13px] text-remetra-text-primary">
              {ingredient.changed && <Text className="font-figtree-semibold text-remetra-primary">Changed: </Text>}
              {ingredient.name}
            </Text>
            <Text className="font-figtree text-[13px] text-remetra-text-tertiary">{ingredient.amount}</Text>
          </ListRow>
        ))}
      </View>
      <Text className="font-figtree text-[13px] leading-[18px] text-remetra-text-secondary">{card.method}</Text>
      {!card.decision && (
        <ButtonRow>
          <PillButton label="Use this version" onPress={onUse} fill />
          <PillButton label="Keep original" onPress={onKeep} variant="ghost" fill />
        </ButtonRow>
      )}
    </CardShell>
  );
}
