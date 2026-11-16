import type { ChatCard, ChatReply, ReplyBlock } from '../types/chat';

/**
 * Local stand-in for POST /chat until the backend returns structured replies.
 * Replies mirror the Ask Remetra designs and use the design's demo data
 * (week 3 update, onion & garlic, lemon herb salmon, celiac + shellfish allergy).
 */

export const SAFETY_CARD: Extract<ChatCard, { type: 'safety' }> = {
  type: 'safety',
  title: 'Get emergency care now',
  body: 'If you have swelling of your lips, tongue or throat, or trouble breathing, call emergency services.',
  actionLabel: 'Call emergency services',
  phoneNumber: '911',
};

export const SAFETY_FOLLOW_UP =
  'I won’t use this as data for your results. When you’re safe, you can log what happened.';

const EMERGENCY_PATTERNS = [
  /\b(can'?t|cannot|unable to|trouble|hard to) breath/,
  /\bthroat\b.*\b(closing|swell|swollen|tight)/,
  /\b(lips?|tongue|face|mouth)\b.*\b(swell|swollen|puff)/,
  /\bswell\w* (of|in|on) (my |the )?(lips?|tongue|face|mouth|throat)/,
  /\banaphyla/,
  /\bepi ?pen\b/,
  /\bchest (pain|pressure|tight)/,
  /\b(passed|passing) out\b|\bfaint(ed|ing)\b/,
  /\b(kill|hurt|harm) myself\b|\bsuicid/,
];

const GLUTEN_FOODS = /\b(sandwich|bread|toast|wrap|burger|pasta|noodle|pizza|bagel|cracker|muffin)\b/;
const SHELLFISH = /\b(shrimp|prawns?|shellfish|crab|lobster|oysters?|scallops?|clams?|mussels?)\b/;
const STILL_LEARNING_FOODS = /\b(spicy food|spicy|dairy|coffee|alcohol|citrus|red meat|beans|lentils|eggs?|soy)\b/;
const SYMPTOM_WORDS: Record<string, string> = {
  bloat: 'Bloating',
  cramp: 'Cramping',
  nause: 'Nausea',
  headache: 'Headache',
  itch: 'Itching',
  ache: 'Aching',
  pain: 'Pain',
  tired: 'Fatigue',
  fatigue: 'Fatigue',
};

const text = (value: string): ReplyBlock => ({ type: 'text', text: value });
const card = (value: ChatCard): ReplyBlock => ({ type: 'card', card: value });
const suggestions = (...items: string[]): ReplyBlock => ({ type: 'suggestions', items });
const answer = (...blocks: ReplyBlock[]): ChatReply => ({ kind: 'answer', blocks });

const INSIGHT_REPLY = answer(
  card({
    type: 'insight',
    title: 'Onion & garlic family',
    evidence: [
      'Tue Oct 8 · Creamy tomato pasta, bloating that evening',
      'Sat Oct 12 · Red lentil soup, cramping later',
      'Oct 17–19 · Garlic-oil swaps, calm evenings',
    ],
  }),
  text('That’s a pattern in your logs, not a diagnosis. It’s worth talking through with your clinician or dietitian.'),
  suggestions('Why might this happen?', 'What can I do next?')
);

const TREND_REPLY = answer(
  card({
    type: 'symptom_calendar',
    title: 'Your last 4 weeks · Sep 30 to Oct 26',
    weeks: [
      ['symptoms', 'clear', 'symptoms', 'clear', 'symptoms', 'clear', 'not_logged'],
      ['clear', 'symptoms', 'clear', 'symptoms', 'clear', 'clear', 'not_logged'],
      ['clear', 'clear', 'symptoms', 'clear', 'clear', 'clear', 'clear'],
      ['clear', 'clear', 'clear', 'clear', 'symptoms', 'clear', 'not_logged'],
    ],
  }),
  text(
    'Symptoms showed up on fewer days in weeks 3 and 4 than in week 1, and they’ve felt milder. Unlogged days aren’t counted.'
  ),
  suggestions('Which weeks were hardest?', 'Summarize for my dietitian')
);

const RECIPE_REPLY = answer(
  text('Here’s a 20-minute version of tonight’s dinner. Same ingredients, faster method.'),
  card({
    type: 'recipe',
    durationLabel: '20 minutes',
    title: 'Lemon herb salmon, 20-minute version',
    ingredients: [
      { name: 'Salmon fillets, cut into strips', amount: '2' },
      { name: 'Microwave jasmine rice', amount: '1 pouch', changed: true },
      { name: 'Green beans, lemon, dill', amount: 'as before' },
    ],
    method: 'Pan-sear the salmon strips 3 minutes a side while the beans steam, then finish with lemon and dill.',
  })
);

const IDEAS_REPLY = answer(
  text('Thai food can work well for you. A few ideas that fit your plan:'),
  card({
    type: 'ideas',
    title: 'Good options to ask about',
    ideas: [
      { kind: 'try', text: 'Grilled chicken with sticky rice. Ask if the marinade has garlic.' },
      { kind: 'try', text: 'Coconut curry with chicken, no onion and no shrimp paste.' },
      { kind: 'ask', text: 'Oyster sauce is shellfish. Ask the kitchen to leave it out.' },
      { kind: 'ask', text: 'Soy sauce usually has wheat. Ask for tamari instead.' },
    ],
  }),
  text('Whatever you end up ordering, log it tonight and it still counts.'),
  suggestions('Any travel tips?')
);

const SUMMARY_REPLY = answer(
  text('Here’s a summary for your dietitian. Review it first, then share.'),
  card({
    type: 'summary',
    eyebrow: 'Remetra summary',
    title: 'Sep 30 to Oct 24',
    sections: [
      { title: 'Logging', body: 'Logged on 23 of 25 days, mostly in the evening.' },
      { title: 'Symptoms', body: 'Bloating and cramping 2–4 hours after lunch. Milder in weeks 3–4.' },
      {
        title: 'Weekly insights',
        body: 'Likely trigger: onion & garlic. Looks fine: dairy, eggs, rice, poultry, citrus, coffee.',
      },
      { title: 'Profile', body: 'Celiac disease. Shellfish allergy.' },
    ],
    disclaimer: 'These are patterns in your logs, not a diagnosis.',
  })
);

export const WEEKLY_UPDATE_BLOCKS: ReplyBlock[] = [
  card({
    type: 'weekly_update',
    eyebrow: 'Your week 3 update is ready',
    title: 'One new likely trigger and six groups that look fine',
    counts: { likelyTrigger: 1, looksFine: 6, stillLearning: 20 },
  }),
  text('Onion & garlic family is now a likely trigger, and six food groups look fine. Want me to walk you through it?'),
  suggestions('Walk me through it', 'Not now'),
];

const FALLBACK_REPLY = answer(
  text('I can help with your own logs, insights and meal ideas. Try asking about your symptoms, a meal, or how things have changed.'),
  suggestions('Have my symptoms improved?', 'I only have 20 minutes', 'I had a turkey sandwich around 1')
);

type PendingStep =
  | { kind: 'gluten_check'; food: string; loggedAt: Date }
  | { kind: 'symptom_time'; feeling: string; intensity: number };

function normalize(message: string): string {
  return message.toLowerCase().replace(/[’']/g, "'").trim();
}

function capitalize(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function mealFor(date: Date): string {
  const hour = date.getHours();
  if (hour < 11) return 'Breakfast';
  if (hour < 16) return 'Lunch';
  if (hour < 21) return 'Dinner';
  return 'Snack';
}

/** "around 1", "at 2 pm", "12:30" -> today at that time. Bare 1–6 are read as afternoon. */
export function parseTime(message: string, now = new Date()): Date | null {
  const match = message.match(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b/i);
  if (!match) return null;
  let hour = Number(match[1]);
  const minute = Number(match[2] ?? 0);
  const meridiem = match[3]?.toLowerCase();
  if (hour > 23 || minute > 59) return null;
  if (meridiem === 'pm' && hour < 12) hour += 12;
  if (meridiem === 'am' && hour === 12) hour = 0;
  if (!meridiem && hour >= 1 && hour <= 6) hour += 12;
  const date = new Date(now);
  date.setHours(hour, minute, 0, 0);
  return date;
}

function parseFood(message: string): string | null {
  const match = message.match(
    /\b(?:i had|i ate|had|ate)\s+(?:a |an |some |the )?(.+?)(?:\s+(?:around|at|for|about)\b.*)?$/i
  );
  return match ? capitalize(match[1].trim()) : null;
}

function parseSymptom(message: string): string | null {
  const lower = normalize(message);
  const key = Object.keys(SYMPTOM_WORDS).find((word) => lower.includes(word));
  return key ? SYMPTOM_WORDS[key] : null;
}

function parseIntensity(message: string): number {
  const match = message.match(/\b(10|[1-9])\b(?!\s*(am|pm|:))/i);
  return match ? Number(match[1]) : 5;
}

function draftReply(food: string, loggedAt: Date): ChatReply {
  return answer(
    text('Thanks. Here’s the entry. Check it and save.'),
    card({ type: 'draft_food', food, meal: mealFor(loggedAt), loggedAt: loggedAt.toISOString(), status: 'draft' })
  );
}

export function isEmergency(message: string): boolean {
  const lower = normalize(message);
  return EMERGENCY_PATTERNS.some((pattern) => pattern.test(lower));
}

export function createMockChatEngine() {
  let pending: PendingStep | null = null;

  function resolvePending(message: string, lower: string): ChatReply | null {
    if (!pending) return null;
    const step = pending;
    pending = null;

    if (step.kind === 'gluten_check') {
      if (/^(yes|yeah|yep|it was|gluten)/.test(lower)) {
        const bread = message.match(/gluten[- ]free\s+[a-z]+/i)?.[0] ?? 'gluten-free';
        return draftReply(`${step.food}, ${bread.toLowerCase()}`, step.loggedAt);
      }
      return draftReply(step.food, step.loggedAt);
    }

    const startedAt = parseTime(message) ?? new Date();
    return answer(
      card({
        type: 'symptom_entry',
        feeling: step.feeling,
        where: 'Stomach',
        intensity: step.intensity,
        startedAt: startedAt.toISOString(),
        status: 'saving',
      })
    );
  }

  function reply(message: string): ChatReply {
    const lower = normalize(message);

    if (isEmergency(message)) {
      pending = null;
      return { kind: 'emergency', blocks: [card(SAFETY_CARD), text(SAFETY_FOLLOW_UP)] };
    }

    const resolved = resolvePending(message, lower);
    if (resolved) return resolved;

    if (/how likely|percent|chance|probab|score|odds/.test(lower)) {
      return answer(
        text(
          'I don’t share percentages or scores, because they can be misleading with this kind of data. In your week 3 update, onion & garlic is labeled a likely trigger.'
        ),
        card({ type: 'likely_trigger_tag' })
      );
    }

    if (/\btrigger\b/.test(lower) && STILL_LEARNING_FOODS.test(lower) && !/onion|garlic/.test(lower)) {
      const food = capitalize(lower.match(STILL_LEARNING_FOODS)?.[0] ?? 'That food');
      return answer(
        text(`It’s too early to say. ${food} is still being learned, and results only change in your weekly update.`),
        card({ type: 'next_update', label: 'Next weekly update', when: 'Sunday morning' })
      );
    }

    if (/walk me through/.test(lower) || (/onion|garlic/.test(lower) && /trigger|why/.test(lower))) {
      return INSIGHT_REPLY;
    }

    if (/why might this happen/.test(lower)) {
      return answer(
        text(
          'Your logs show the pattern, not the reason behind it. A clinician or dietitian can help you look into why.'
        ),
        suggestions('What can I do next?')
      );
    }

    if (/what can i do next/.test(lower)) {
      return answer(
        text(
          'Keep logging the way you have been. Your weekly update will show whether the pattern holds, and you can bring it to your clinician or dietitian.'
        ),
        suggestions('Summarize for my dietitian')
      );
    }

    if (/^not now/.test(lower)) {
      return answer(text('No problem. Your update will be here whenever you want to look.'));
    }

    if (/weekly update|week 3 update|my update/.test(lower)) {
      return answer(...WEEKLY_UPDATE_BLOCKS);
    }

    if (/(add|put|include|with)\b/.test(lower) && SHELLFISH.test(lower)) {
      const item = lower.match(SHELLFISH)?.[0] ?? 'that';
      return answer(
        text(
          `I can’t add ${item}, since you’ve told Remetra you’re allergic to shellfish. A second salmon fillet or a soft-boiled egg would both add protein.`
        ),
        suggestions('Add a soft-boiled egg')
      );
    }

    if (/soft-boiled egg|second salmon/.test(lower)) {
      return answer(text('Done. Tonight’s dinner now includes a soft-boiled egg for extra protein.'));
    }

    if (/why did you (pick|choose)|why this dinner|why (this|that) (meal|recipe)/.test(lower)) {
      return answer(
        text(
          'Each idea is chosen to help Remetra learn about your body. I can’t say more without affecting your results, but I can change it to fit your time or taste.'
        ),
        suggestions('I only have 20 minutes')
      );
    }

    if (/\d+\s*min|quick|faster|in a hurry|adapt|tonight's dinner/.test(lower)) {
      return RECIPE_REPLY;
    }

    if (/thai|restaurant|order|eat out|eating out|takeout|take-out/.test(lower)) {
      return IDEAS_REPLY;
    }

    if (/travel/.test(lower)) {
      return answer(
        text(
          'Pack a couple of foods you know sit well with you, and check menus before you go. Log as you travel and it all still counts.'
        )
      );
    }

    if (/summar|dietitian|appointment|doctor|clinician/.test(lower)) {
      return SUMMARY_REPLY;
    }

    if (/hardest|worst week/.test(lower)) {
      return answer(
        text('Week 1 was the hardest, with symptoms on more of your logged days than any other week. Things eased from week 3.'),
        suggestions('Summarize for my dietitian')
      );
    }

    if (/improv|better|worse|over time|trend|progress|change/.test(lower)) {
      return TREND_REPLY;
    }

    const feeling = parseSymptom(message);
    if (feeling && /felt|feel|feeling|been|have|had|got/.test(lower)) {
      pending = { kind: 'symptom_time', feeling, intensity: parseIntensity(message) };
      return answer(text('Sorry it’s been uncomfortable. About what time did it start?'));
    }

    const food = parseFood(message);
    if (food) {
      const loggedAt = parseTime(message) ?? new Date();
      if (GLUTEN_FOODS.test(food.toLowerCase()) && !/gluten[- ]free/i.test(food)) {
        pending = { kind: 'gluten_check', food, loggedAt };
        return answer(text('Quick check: you have celiac disease. Was it on gluten-free bread?'));
      }
      return draftReply(food, loggedAt);
    }

    return FALLBACK_REPLY;
  }

  return { reply };
}
