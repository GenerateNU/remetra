import { createMockChatEngine, isEmergency, parseTime } from '../mock_chat_engine';
import type { ChatCard, ChatReply } from '../../types/chat';

const cardsOf = (reply: ChatReply): ChatCard[] =>
  reply.blocks.flatMap((block) => (block.type === 'card' ? [block.card] : []));
const textsOf = (reply: ChatReply): string[] =>
  reply.blocks.flatMap((block) => (block.type === 'text' ? [block.text] : []));
const suggestionsOf = (reply: ChatReply): string[] =>
  reply.blocks.flatMap((block) => (block.type === 'suggestions' ? block.items : []));

describe('mock chat engine', () => {
  it('explains an insight with an insight card and follow-up chips (screen 02)', () => {
    const reply = createMockChatEngine().reply('Why is onion & garlic a likely trigger?');

    expect(cardsOf(reply)[0]).toMatchObject({ type: 'insight', title: 'Onion & garlic family' });
    expect(suggestionsOf(reply)).toEqual(['Why might this happen?', 'What can I do next?']);
  });

  it('shows the symptom calendar for change over time (screen 03)', () => {
    const reply = createMockChatEngine().reply('Have my symptoms improved since September?');
    const calendar = cardsOf(reply)[0];

    expect(calendar.type).toBe('symptom_calendar');
    expect(calendar.type === 'symptom_calendar' && calendar.weeks).toHaveLength(4);
  });

  it('adapts the recipe (screen 04) and suggests restaurant ideas (screen 05)', () => {
    const engine = createMockChatEngine();

    expect(cardsOf(engine.reply('I only have 20 minutes'))[0]).toMatchObject({ type: 'recipe', durationLabel: '20 minutes' });
    expect(cardsOf(engine.reply('What could I order at a Thai place?'))[0]).toMatchObject({ type: 'ideas' });
  });

  it('runs the log-by-chat flow with a gluten check before the draft (screen 06)', () => {
    const engine = createMockChatEngine();

    const question = engine.reply('I had a turkey sandwich around 1');
    const draft = engine.reply('Yes, gluten-free bread');

    expect(textsOf(question)[0]).toContain('celiac disease');
    expect(cardsOf(draft)[0]).toMatchObject({
      type: 'draft_food',
      food: 'Turkey sandwich, gluten-free bread',
      meal: 'Lunch',
      status: 'draft',
    });
  });

  it('asks for a start time and then returns a symptom entry (screen 07)', () => {
    const engine = createMockChatEngine();

    const question = engine.reply('Felt bloated after lunch, maybe a 4');
    const entry = engine.reply('Around 2 PM');

    expect(textsOf(question)[0]).toContain('About what time did it start?');
    expect(cardsOf(entry)[0]).toMatchObject({ type: 'symptom_entry', feeling: 'Bloating', intensity: 4 });
  });

  it('returns a dietitian summary (screen 08)', () => {
    const reply = createMockChatEngine().reply('Summarize my last month for my dietitian');

    expect(cardsOf(reply)[0]).toMatchObject({ type: 'summary', title: 'Sep 30 to Oct 24' });
  });

  it('refuses to add an allergen and offers an alternative (screen 09)', () => {
    const reply = createMockChatEngine().reply('Add shrimp to tonight’s dinner');

    expect(textsOf(reply)[0]).toContain('allergic to shellfish');
    expect(suggestionsOf(reply)).toEqual(['Add a soft-boiled egg']);
  });

  it('says it is too early for still-learning foods and never gives numbers (screen 10)', () => {
    const engine = createMockChatEngine();

    expect(cardsOf(engine.reply('Is spicy food my trigger?'))[0]).toMatchObject({ type: 'next_update' });
    expect(cardsOf(engine.reply('How likely is it that garlic is the problem?'))[0]).toEqual({
      type: 'likely_trigger_tag',
    });
  });

  it('shows the safety banner for emergencies (screen 11)', () => {
    const reply = createMockChatEngine().reply('My lips are swelling after lunch');

    expect(reply.kind).toBe('emergency');
    expect(cardsOf(reply)[0]).toMatchObject({ type: 'safety', phoneNumber: '911' });
  });

  it('shows the weekly update when asked (screen 12)', () => {
    const reply = createMockChatEngine().reply('Show my weekly update');

    expect(cardsOf(reply)[0]).toMatchObject({ type: 'weekly_update', counts: { likelyTrigger: 1 } });
  });

  it('falls back to starter suggestions for unrelated messages', () => {
    const reply = createMockChatEngine().reply('hello there');

    expect(suggestionsOf(reply).length).toBeGreaterThan(0);
  });
});

describe('parseTime', () => {
  const now = new Date(2026, 9, 20, 9, 0);

  it('reads bare afternoon hours as PM', () => {
    expect(parseTime('around 1', now)?.getHours()).toBe(13);
  });

  it('respects am/pm and minutes', () => {
    const time = parseTime('at 8:30 am', now);
    expect([time?.getHours(), time?.getMinutes()]).toEqual([8, 30]);
  });

  it('returns null without a time', () => {
    expect(parseTime('no time here', now)).toBeNull();
  });
});

describe('isEmergency', () => {
  it.each(['I can’t breathe', 'my throat is closing', 'my tongue feels swollen'])('flags "%s"', (message) => {
    expect(isEmergency(message)).toBe(true);
  });

  it('ignores ordinary symptoms', () => {
    expect(isEmergency('felt bloated after lunch')).toBe(false);
  });
});
