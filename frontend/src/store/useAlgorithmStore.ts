import { create } from 'zustand';
import { algorithmService } from '../api/algorithm_service';
import { apiClient } from '../api/client';
import { Association } from '../components/AssociationCard';

export interface SymptomSummary {
  id: string;
  name: string;
}

export interface EnrichedAssociation extends Association {
  symptom_id: string;
}

interface AlgorithmState {
  associationsBySymptom: Record<string, EnrichedAssociation[]>;
  symptoms: SymptomSummary[];
  isLoading: boolean;
  error: string | null;
}

interface AlgorithmActions {
  fetchAssociations: (userId: string) => Promise<void>;
  runAlgorithm: (userId: string) => Promise<void>;
}

type AlgorithmStore = AlgorithmState & AlgorithmActions;

const initialState: AlgorithmState = {
  associationsBySymptom: {},
  symptoms: [],
  isLoading: false,
  error: null,
};

async function buildLookupMaps(): Promise<{
  foodMap: Record<string, string>;
  symptomMap: Record<string, string>;
}> {
  const [foodsRes, symptomsRes] = await Promise.all([
    apiClient.get('/food/'),
    apiClient.get('/symptom/'),
  ]);

  const foodMap: Record<string, string> = {};
  for (const f of foodsRes.data) {
    foodMap[f.id] = f.name;
  }

  const symptomMap: Record<string, string> = {};
  for (const s of symptomsRes.data) {
    symptomMap[s.id] = s.name;
  }

  return { foodMap, symptomMap };
}

function enrichAndGroup(
  rawAssociations: Awaited<ReturnType<typeof algorithmService.getAssociations>>,
  foodMap: Record<string, string>,
  symptomMap: Record<string, string>,
): {
  associationsBySymptom: Record<string, EnrichedAssociation[]>;
  symptoms: SymptomSummary[];
} {
  const associationsBySymptom: Record<string, EnrichedAssociation[]> = {};
  const symptomsSeen = new Map<string, string>();

  for (const assoc of rawAssociations) {
    const food_name = foodMap[assoc.associated_food_id] ?? assoc.associated_food_id;
    const symptom_name = symptomMap[assoc.symptom_id] ?? assoc.symptom_id;
    symptomsSeen.set(assoc.symptom_id, symptom_name);

    if (!associationsBySymptom[assoc.symptom_id]) {
      associationsBySymptom[assoc.symptom_id] = [];
    }
    associationsBySymptom[assoc.symptom_id].push({
      symptom_id: assoc.symptom_id,
      food_name,
      trigger_rate: assoc.key_metrics.trigger_rate,
      base_rate: assoc.key_metrics.base_rate,
      exposures: assoc.key_metrics.exposures,
      average_intensity: assoc.key_metrics.average_intensity,
      fishers_p_value: assoc.key_metrics.fishers_p_value,
    });
  }

  const symptoms: SymptomSummary[] = Array.from(symptomsSeen.entries()).map(([id, name]) => ({
    id,
    name,
  }));

  return { associationsBySymptom, symptoms };
}

export const useAlgorithmStore = create<AlgorithmStore>((set) => ({
  ...initialState,

  fetchAssociations: async (userId: string) => {
    set({ isLoading: true, error: null });
    try {
      const [rawAssociations, { foodMap, symptomMap }] = await Promise.all([
        algorithmService.getAssociations(userId),
        buildLookupMaps(),
      ]);

      const { associationsBySymptom, symptoms } = enrichAndGroup(rawAssociations, foodMap, symptomMap);
      set({ associationsBySymptom, symptoms, isLoading: false });
    } catch (err: any) {
      set({ error: err.message ?? 'Failed to load associations', isLoading: false });
    }
  },

  runAlgorithm: async (userId: string) => {
    set({ isLoading: true, error: null });
    try {
      const [rawAssociations, { foodMap, symptomMap }] = await Promise.all([
        algorithmService.analyze({ user_id: userId }),
        buildLookupMaps(),
      ]);

      const { associationsBySymptom, symptoms } = enrichAndGroup(rawAssociations.associations, foodMap, symptomMap);
      set({ associationsBySymptom, symptoms, isLoading: false });
    } catch (err: any) {
      set({ error: err.message ?? 'Failed to run algorithm', isLoading: false });
    }
  },
}));
