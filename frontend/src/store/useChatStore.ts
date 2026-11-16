import { create } from 'zustand';
import { CHAT_USES_MOCK, chatService, ChatSession } from '../api/chat_service';
import { ApiError } from '../api/client';
import { WEEKLY_UPDATE_BLOCKS } from '../api/mock_chat_engine';
import { foodLogService } from '../api/food_log_service';
import { symptomLogService } from '../api/symptom_log_service';
import { useAuthStore } from './useAuthStore';
import { useBankStore } from './bankStore';
import { useUIStore } from './uiStore';
import { formatClockTime, formatDayLabel } from '../utils/time';
import type { AskEntry, CardItem, ChatCard, ReplyBlock, ThreadItem, ThreadMarker } from '../types/chat';

export const SAVED_TOAST = 'Saved to today’s log';
const ERROR_REPLY = 'Sorry, I couldn’t answer just now. Please try again in a moment.';

// The mock uses the design's demo data; the live chat only knows the user's own logs.
export const ASK_MARKERS = {
  insights: { kind: 'context', label: CHAT_USES_MOCK ? 'From your week 3 update' : 'From your insights' },
  recipe: { kind: 'context', label: 'About: Lemon herb salmon' },
  log: { kind: 'context', label: CHAT_USES_MOCK ? 'From today’s log' : 'From your logs' },
  newConversation: { kind: 'day', label: 'New conversation' },
} satisfies Record<string, ThreadMarker>;

let idCounter = 0;
const newId = () => `ask-${Date.now()}-${idCounter++}`;
const toItems = (blocks: ReplyBlock[]): ThreadItem[] => blocks.map((block) => ({ id: newId(), ...block }));

export function ingredientsFrom(food: string): string[] {
  return food
    .split(/,| with | and /i)
    .map((part) => part.trim().toLowerCase())
    .filter(Boolean);
}

function requireUsername(): string {
  const username = useAuthStore.getState().user.name;
  if (!username) throw new Error('Not signed in');
  return username;
}

async function saveFoodLog(food: string, loggedAt: Date): Promise<void> {
  const username = requireUsername();
  const bank = useBankStore.getState();
  if (bank.foods.length === 0) await bank.fetchFoods();

  const existing = useBankStore.getState().foods.find((item) => item.name.toLowerCase() === food.toLowerCase());
  const foodId = existing?.id ?? (await bank.addFood(food, ingredientsFrom(food)));
  if (!foodId) throw new Error('Could not create food');

  await foodLogService.createFoodLog({
    food_id: foodId,
    quantity: '1 serving(s)',
    timestamp: loggedAt.toISOString(),
    username,
  });
  useUIStore.getState().notifyLogCreated();
}

async function saveSymptomLog(card: Extract<ChatCard, { type: 'symptom_entry' }>): Promise<void> {
  const username = requireUsername();
  const bank = useBankStore.getState();
  if (bank.symptoms.length === 0) await bank.fetchSymptoms();

  const existing = useBankStore
    .getState()
    .symptoms.find(
      (item) =>
        item.name.toLowerCase() === card.feeling.toLowerCase() &&
        item.location.toLowerCase() === card.where.toLowerCase()
    );
  const symptomId = existing?.id ?? (await bank.addSymptom(card.feeling, card.where, card.feeling));
  if (!symptomId) throw new Error('Could not create symptom');

  await symptomLogService.createSymptomLog({
    symptom_id: symptomId,
    intensity: card.intensity,
    timestamp: card.startedAt,
    username,
  });
  useUIStore.getState().notifyLogCreated();
}

interface ChatState {
  entry: AskEntry | null;
  items: ThreadItem[];
  isReplying: boolean;
  toast: { id: number; message: string } | null;
  session: ChatSession;
  start: (entry?: AskEntry) => void;
  send: (text: string, marker?: ThreadMarker) => Promise<void>;
  saveDraft: (id: string) => Promise<void>;
  markDraftSaved: (id: string, food: string, loggedAt: Date) => void;
  saveSymptom: (id: string) => Promise<void>;
  decideRecipe: (id: string, decision: 'used' | 'kept') => void;
  showToast: (message: string) => void;
  dismissToast: () => void;
}

export const useChatStore = create<ChatState>((set, get) => {
  const findCard = <T extends ChatCard['type']>(id: string, type: T) => {
    const item = get().items.find((entry) => entry.id === id);
    if (item?.type !== 'card' || item.card.type !== type) return null;
    return item.card as Extract<ChatCard, { type: T }>;
  };

  const replaceItem = (id: string, next: ThreadItem) =>
    set((state) => ({ items: state.items.map((item) => (item.id === id ? next : item)) }));

  const patchCard = (id: string, patch: Partial<ChatCard>) =>
    set((state) => ({
      items: state.items.map((item) =>
        item.id === id && item.type === 'card' ? ({ ...item, card: { ...item.card, ...patch } } as CardItem) : item
      ),
    }));

  const appendReply = (blocks: ReplyBlock[]) => set((state) => ({ items: [...state.items, ...toItems(blocks)] }));

  return {
    entry: null,
    items: [],
    isReplying: false,
    toast: null,
    session: chatService.createSession(),

    start: (entry) => {
      const items: ThreadItem[] =
        entry === 'weekly_update' && CHAT_USES_MOCK
          ? [
              { id: newId(), type: 'marker', marker: { kind: 'day', label: formatDayLabel(new Date()) } },
              ...toItems(WEEKLY_UPDATE_BLOCKS),
            ]
          : [];
      set({ entry: entry ?? null, items, isReplying: false, toast: null, session: chatService.createSession() });
    },

    send: async (text, marker) => {
      const message = text.trim();
      const { items, entry, session, isReplying } = get();
      if (!message || isReplying) return;

      const additions: ThreadItem[] = [];
      if (items.length === 0) {
        const opening = marker ?? (entry && entry !== 'weekly_update' ? ASK_MARKERS[entry] : undefined);
        if (opening) additions.push({ id: newId(), type: 'marker', marker: opening });
      }
      additions.push({ id: newId(), type: 'user', text: message });
      set({ items: [...items, ...additions], isReplying: true });

      try {
        const reply = await session.send(message);
        if (get().session !== session) return;
        const replyItems = toItems(reply.blocks);
        set((state) => ({ items: [...state.items, ...replyItems], isReplying: false }));
        replyItems
          .filter((item) => item.type === 'card' && item.card.type === 'symptom_entry')
          .forEach((item) => void get().saveSymptom(item.id));
      } catch (err) {
        if (get().session !== session) return;
        const text = err instanceof ApiError ? err.message : ERROR_REPLY;
        set((state) => ({
          items: [...state.items, { id: newId(), type: 'text', text }],
          isReplying: false,
        }));
      }
    },

    saveDraft: async (id) => {
      const draft = findCard(id, 'draft_food');
      if (!draft || draft.status === 'saving') return;
      patchCard(id, { status: 'saving' });
      try {
        await saveFoodLog(draft.food, new Date(draft.loggedAt));
        get().markDraftSaved(id, draft.food, new Date(draft.loggedAt));
      } catch {
        patchCard(id, { status: 'error' });
      }
    },

    markDraftSaved: (id, food, loggedAt) => {
      replaceItem(id, {
        id,
        type: 'card',
        card: { type: 'saved', text: `Saved: ${food} · ${formatClockTime(loggedAt)}` },
      });
      get().showToast(SAVED_TOAST);
    },

    saveSymptom: async (id) => {
      const entry = findCard(id, 'symptom_entry');
      if (!entry) return;
      patchCard(id, { status: 'saving' });
      try {
        await saveSymptomLog(entry);
        patchCard(id, { status: 'saved' });
        get().showToast(SAVED_TOAST);
      } catch {
        patchCard(id, { status: 'error' });
      }
    },

    decideRecipe: (id, decision) => {
      if (!findCard(id, 'recipe')) return;
      patchCard(id, { decision });
      appendReply([
        {
          type: 'text',
          text:
            decision === 'used'
              ? 'Done. Tonight’s dinner is now the 20-minute version.'
              : 'No problem. Tonight’s dinner stays as planned.',
        },
      ]);
    },

    showToast: (message) => set({ toast: { id: idCounter++, message } }),
    dismissToast: () => set({ toast: null }),
  };
});
