import { create } from 'zustand';

export const CELIAC = 'Celiac disease';
export const NONE_CONDITION = 'None or prefer not to say';
export const LOCKED_GLUTEN = 'Gluten';

export const CONDITION_OPTIONS = [
  CELIAC,
  'IBS',
  'IBD (Crohn’s or ulcerative colitis)',
  'Another autoimmune condition',
  NONE_CONDITION,
] as const;

export const SUSPICION_OPTIONS = [
  'Onion & garlic',
  'Dairy',
  'Coffee',
  'Alcohol',
  'Spicy food',
  'Beans & lentils',
  'Red meat',
  'Citrus',
] as const;

export const REGULAR_OPTIONS = [
  'Dairy',
  'Eggs',
  'Fish',
  'Poultry',
  'Red meat',
  'Legumes',
  'Soy',
  'Tree nuts',
  'Peanuts',
  'Coffee',
  'Alcohol',
] as const;

export const EXCLUSION_CATALOG = [
  'Shellfish',
  'Mushrooms',
  'Pork',
  'Dairy',
  'Eggs',
  'Fish',
  'Peanuts',
  'Tree nuts',
  'Soy',
  'Sesame',
  'Nightshades',
  'Onion & garlic',
  'Spicy food',
  'Beans & lentils',
  'Red meat',
  'Citrus',
  'Alcohol',
  'Coffee',
  LOCKED_GLUTEN,
] as const;

export interface Exclusion {
  name: string;
  allergic: boolean;
}

interface OnboardingState {
  conditions: string[];
  exclusions: Exclusion[];
  suspicions: string[];
  regulars: string[];
  toggleCondition: (name: string) => void;
  addExclusion: (name: string) => void;
  setExclusionAllergic: (name: string, allergic: boolean) => void;
  toggleSuspicion: (name: string) => void;
  toggleRegular: (name: string) => void;
  reset: () => void;
}

const empty = {
  conditions: [] as string[],
  exclusions: [] as Exclusion[],
  suspicions: [] as string[],
  regulars: [] as string[],
};

export const useOnboardingStore = create<OnboardingState>((set) => ({
  ...empty,

  toggleCondition: (name) =>
    set((state) => {
      const selected = state.conditions.includes(name);
      let conditions: string[];
      if (name === NONE_CONDITION) {
        conditions = selected ? [] : [NONE_CONDITION];
      } else if (selected) {
        conditions = state.conditions.filter((item) => item !== name);
      } else {
        conditions = [...state.conditions.filter((item) => item !== NONE_CONDITION), name];
      }
      const exclusions = conditions.includes(CELIAC)
        ? state.exclusions.filter((item) => item.name !== LOCKED_GLUTEN)
        : state.exclusions;
      return { conditions, exclusions };
    }),

  addExclusion: (name) =>
    set((state) => {
      if (state.exclusions.some((item) => item.name === name)) return state;
      if (name === LOCKED_GLUTEN && state.conditions.includes(CELIAC)) return state;
      return { exclusions: [...state.exclusions, { name, allergic: false }] };
    }),

  setExclusionAllergic: (name, allergic) =>
    set((state) => ({
      exclusions: state.exclusions.map((item) =>
        item.name === name ? { ...item, allergic } : item
      ),
    })),

  toggleSuspicion: (name) =>
    set((state) => ({
      suspicions: state.suspicions.includes(name)
        ? state.suspicions.filter((item) => item !== name)
        : [...state.suspicions, name],
    })),

  toggleRegular: (name) =>
    set((state) => ({
      regulars: state.regulars.includes(name)
        ? state.regulars.filter((item) => item !== name)
        : [...state.regulars, name],
    })),

  reset: () => set(empty),
}));
