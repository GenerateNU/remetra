// Where Ask Remetra was opened from. Drives the context chip and composer placeholder.
export type AskEntry = 'insights' | 'recipe' | 'log' | 'weekly_update';

export type ThreadMarker =
  | { kind: 'context'; label: string }
  | { kind: 'day'; label: string };

export type DayStatus = 'symptoms' | 'clear' | 'not_logged';

export interface RecipeIngredient {
  name: string;
  amount: string;
  changed?: boolean;
}

export type ChatCard =
  | { type: 'insight'; title: string; evidence: string[] }
  | { type: 'symptom_calendar'; title: string; weeks: DayStatus[][] }
  | {
      type: 'recipe';
      durationLabel: string;
      title: string;
      ingredients: RecipeIngredient[];
      method: string;
      decision?: 'used' | 'kept';
    }
  | { type: 'ideas'; title: string; ideas: { kind: 'try' | 'ask'; text: string }[] }
  | { type: 'draft_food'; food: string; meal: string; loggedAt: string; status: 'draft' | 'saving' | 'error' }
  | { type: 'saved'; text: string }
  | {
      type: 'symptom_entry';
      feeling: string;
      where: string;
      intensity: number;
      startedAt: string;
      status: 'saving' | 'saved' | 'error';
    }
  | { type: 'summary'; eyebrow: string; title: string; sections: { title: string; body: string }[]; disclaimer: string }
  | { type: 'next_update'; label: string; when: string }
  | { type: 'likely_trigger_tag' }
  | { type: 'safety'; title: string; body: string; actionLabel: string; phoneNumber: string }
  | {
      type: 'weekly_update';
      eyebrow: string;
      title: string;
      counts: { likelyTrigger: number; looksFine: number; stillLearning: number };
    };

export type ReplyBlock =
  | { type: 'text'; text: string }
  | { type: 'card'; card: ChatCard }
  | { type: 'suggestions'; items: string[] };

export interface ChatReply {
  kind: 'answer' | 'emergency' | 'refused';
  blocks: ReplyBlock[];
}

export type ThreadItem =
  | { id: string; type: 'marker'; marker: ThreadMarker }
  | { id: string; type: 'user'; text: string }
  | ({ id: string } & ReplyBlock);

export type CardItem = Extract<ThreadItem, { type: 'card' }>;
