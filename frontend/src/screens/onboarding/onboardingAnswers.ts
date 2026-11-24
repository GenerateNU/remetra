import { CELIAC, LOCKED_GLUTEN, NONE_CONDITION } from '../../store/onboardingStore';

export interface OnboardingAnswers {
  disease: string[];
  avoid: string[];
  suspect: string[];
  safe: string[];
}

export function onboardingAnswers(state: {
  conditions: string[];
  exclusions: { name: string }[];
  suspicions: string[];
  regulars: string[];
}): OnboardingAnswers {
  const disease = state.conditions.filter((condition) => condition !== NONE_CONDITION);
  const avoid = state.exclusions.map((item) => item.name);
  if (state.conditions.includes(CELIAC) && !avoid.includes(LOCKED_GLUTEN)) {
    avoid.push(LOCKED_GLUTEN);
  }
  return {
    disease,
    avoid,
    suspect: [...state.suspicions],
    safe: [...state.regulars],
  };
}
