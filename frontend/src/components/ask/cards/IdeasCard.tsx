import { Text } from 'react-native';
import { CardShell, Eyebrow, ListRow } from './CardParts';
import type { ChatCard } from '../../../types/chat';

/** Figma "Ask / Ideas list" (screen 05: restaurant ideas). */
export function IdeasCard({ card }: { card: Extract<ChatCard, { type: 'ideas' }> }) {
  return (
    <CardShell>
      <Eyebrow>{card.title}</Eyebrow>
      {card.ideas.map((idea, index) => (
        <ListRow key={idea.text} first={index === 0} className="items-start gap-2.5">
          <Text
            className={`w-9 font-figtree-bold text-[12px] leading-[18px] ${
              idea.kind === 'try' ? 'text-remetra-fine-line' : 'text-remetra-chip-strong'
            }`}
          >
            {idea.kind === 'try' ? 'Try' : 'Ask'}
          </Text>
          <Text className="flex-1 font-figtree text-[13px] leading-[18px] text-remetra-text-primary">{idea.text}</Text>
        </ListRow>
      ))}
    </CardShell>
  );
}
