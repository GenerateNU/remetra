import { SavedBanner } from './CardParts';
import { DraftFoodCard } from './DraftFoodCard';
import { IdeasCard } from './IdeasCard';
import { InsightCard } from './InsightCard';
import { RecipeCard } from './RecipeCard';
import { LikelyTriggerTag, NextUpdateCard, SafetyBanner, WeeklyUpdateCard } from './SmallCards';
import { SummaryCard } from './SummaryCard';
import { SymptomCalendarCard } from './SymptomCalendarCard';
import { SymptomEntryCard } from './SymptomEntryCard';
import { useChatStore } from '../../../store/useChatStore';
import type { CardItem } from '../../../types/chat';

export function ChatCardView({ item, onEditDraft }: { item: CardItem; onEditDraft: (id: string) => void }) {
  const saveDraft = useChatStore((state) => state.saveDraft);
  const saveSymptom = useChatStore((state) => state.saveSymptom);
  const decideRecipe = useChatStore((state) => state.decideRecipe);
  const showToast = useChatStore((state) => state.showToast);
  const { card } = item;

  switch (card.type) {
    case 'insight':
      return <InsightCard card={card} />;
    case 'symptom_calendar':
      return <SymptomCalendarCard card={card} />;
    case 'recipe':
      return (
        <RecipeCard
          card={card}
          onUse={() => decideRecipe(item.id, 'used')}
          onKeep={() => decideRecipe(item.id, 'kept')}
        />
      );
    case 'ideas':
      return <IdeasCard card={card} />;
    case 'draft_food':
      return <DraftFoodCard card={card} onSave={() => void saveDraft(item.id)} onEdit={() => onEditDraft(item.id)} />;
    case 'saved':
      return <SavedBanner text={card.text} />;
    case 'symptom_entry':
      return <SymptomEntryCard card={card} onRetry={() => void saveSymptom(item.id)} />;
    case 'summary':
      return <SummaryCard card={card} onCopied={() => showToast('Copied to clipboard')} />;
    case 'next_update':
      return <NextUpdateCard card={card} />;
    case 'likely_trigger_tag':
      return <LikelyTriggerTag />;
    case 'safety':
      return <SafetyBanner card={card} />;
    case 'weekly_update':
      return <WeeklyUpdateCard card={card} />;
  }
}
