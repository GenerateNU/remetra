import { ASK_MARKERS, SAVED_TOAST, useChatStore } from '../useChatStore';
import { useAuthStore } from '../useAuthStore';
import { useBankStore } from '../bankStore';
import { foodLogService } from '../../api/food_log_service';
import { symptomLogService } from '../../api/symptom_log_service';
import type { CardItem, ThreadItem } from '../../types/chat';

jest.mock('../../auth/clerkSession', () => ({
  clerkSignIn: jest.fn(),
  clerkSignUp: jest.fn(),
  clerkSignOut: jest.fn(),
}));

jest.mock('../../api/chat_service', () => {
  const { createMockChatEngine } = jest.requireActual('../../api/mock_chat_engine');
  return {
    CHAT_USES_MOCK: true,
    chatService: {
      createSession: () => {
        const engine = createMockChatEngine();
        return { send: async (message: string) => engine.reply(message) };
      },
    },
  };
});

jest.mock('../../api/food_log_service', () => ({ foodLogService: { createFoodLog: jest.fn() } }));
jest.mock('../../api/symptom_log_service', () => ({ symptomLogService: { createSymptomLog: jest.fn() } }));

const mockCreateFoodLog = foodLogService.createFoodLog as jest.Mock;
const mockCreateSymptomLog = symptomLogService.createSymptomLog as jest.Mock;

const cards = (items: ThreadItem[]) => items.filter((item): item is CardItem => item.type === 'card');
const lastCard = () => cards(useChatStore.getState().items).at(-1)!;

describe('useChatStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCreateFoodLog.mockResolvedValue({});
    mockCreateSymptomLog.mockResolvedValue({});
    useAuthStore.setState((state) => ({ user: { ...state.user, name: 'nicole' } }));
    useBankStore.setState({
      foods: [{ id: 'food-1', name: 'Turkey sandwich, gluten-free bread', ingredients: [] }],
      symptoms: [{ id: 'symptom-1', name: 'Bloating', location: 'Stomach', sensation: 'Bloating' }],
    } as Partial<ReturnType<typeof useBankStore.getState>>);
    useChatStore.getState().start();
  });

  it('starts empty, and seeds the weekly update for the weekly_update entry', () => {
    expect(useChatStore.getState().items).toEqual([]);

    useChatStore.getState().start('weekly_update');

    const [marker, card] = useChatStore.getState().items;
    expect(marker).toMatchObject({ type: 'marker', marker: { kind: 'day' } });
    expect(card).toMatchObject({ type: 'card', card: { type: 'weekly_update' } });
  });

  it('opens the thread with the entry marker, then the question and the reply', async () => {
    useChatStore.getState().start('insights');

    await useChatStore.getState().send('Why is onion & garlic a likely trigger?');

    const { items, isReplying } = useChatStore.getState();
    expect(isReplying).toBe(false);
    expect(items[0]).toMatchObject({ type: 'marker', marker: ASK_MARKERS.insights });
    expect(items[1]).toMatchObject({ type: 'user', text: 'Why is onion & garlic a likely trigger?' });
    expect(items[2]).toMatchObject({ type: 'card', card: { type: 'insight' } });
  });

  it('prefers a starter marker over the entry marker and only adds it once', async () => {
    await useChatStore.getState().send('Have my symptoms improved?', ASK_MARKERS.newConversation);
    await useChatStore.getState().send('Which weeks were hardest?', ASK_MARKERS.recipe);

    const markers = useChatStore.getState().items.filter((item) => item.type === 'marker');
    expect(markers).toEqual([expect.objectContaining({ marker: ASK_MARKERS.newConversation })]);
  });

  it('ignores blank messages', async () => {
    await useChatStore.getState().send('   ');

    expect(useChatStore.getState().items).toEqual([]);
  });

  it('saves a draft food entry, replaces it with the saved state and shows the toast', async () => {
    await useChatStore.getState().send('I had a turkey sandwich around 1');
    await useChatStore.getState().send('Yes, gluten-free bread');
    const draft = lastCard();

    await useChatStore.getState().saveDraft(draft.id);

    expect(mockCreateFoodLog).toHaveBeenCalledWith(
      expect.objectContaining({ food_id: 'food-1', username: 'nicole' })
    );
    expect(lastCard().card).toMatchObject({ type: 'saved' });
    expect(lastCard().card.type === 'saved' && lastCard().card).toMatchObject({
      text: expect.stringContaining('Saved: Turkey sandwich, gluten-free bread'),
    });
    expect(useChatStore.getState().toast?.message).toBe(SAVED_TOAST);
  });

  it('marks the draft as failed when saving errors', async () => {
    mockCreateFoodLog.mockRejectedValueOnce(new Error('offline'));
    await useChatStore.getState().send('I had a turkey sandwich around 1');
    await useChatStore.getState().send('Yes, gluten-free bread');

    await useChatStore.getState().saveDraft(lastCard().id);

    expect(lastCard().card).toMatchObject({ type: 'draft_food', status: 'error' });
  });

  it('auto-saves a symptom entry once the start time is given', async () => {
    await useChatStore.getState().send('Felt bloated after lunch, maybe a 4');
    await useChatStore.getState().send('Around 2 PM');
    await new Promise<void>((resolve) => setImmediate(() => resolve()));

    expect(mockCreateSymptomLog).toHaveBeenCalledWith(
      expect.objectContaining({ symptom_id: 'symptom-1', intensity: 4, username: 'nicole' })
    );
    expect(lastCard().card).toMatchObject({ type: 'symptom_entry', status: 'saved' });
  });

  it('records the recipe decision and confirms it', async () => {
    await useChatStore.getState().send('I only have 20 minutes');

    useChatStore.getState().decideRecipe(lastCard().id, 'used');

    expect(lastCard().card).toMatchObject({ type: 'recipe', decision: 'used' });
    expect(useChatStore.getState().items.at(-1)).toMatchObject({ type: 'text' });
  });
});
