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
  minExposures: number;
}

interface AlgorithmActions {
  fetchAssociations: (userId: string) => Promise<void>;
  setMinExposures: (minExposures: number) => void;
  runAlgorithm: (userId: string) => Promise<void>;
}

type AlgorithmStore = AlgorithmState & AlgorithmActions;

async function buildSymptomMap(): Promise<Record<string, string>> {
  const symptomsRes = await apiClient.get('/symptom/');
  const symptomMap: Record<string, string> = {};
  for (const s of symptomsRes.data) {
    symptomMap[s.id] = s.name;
  }
  return symptomMap;
}

function enrichAndGroup(
  rawAssociations: Awaited<ReturnType<typeof algorithmService.getAssociations>>,
  symptomMap: Record<string, string>,
): {
  associationsBySymptom: Record<string, EnrichedAssociation[]>;
  symptoms: SymptomSummary[];
} {
  const associationsBySymptom: Record<string, EnrichedAssociation[]> = {};
  const symptomsSeen = new Map<string, string>();

  for (const assoc of rawAssociations) {
    const symptom_name = symptomMap[assoc.symptom_id] ?? assoc.symptom_id;
    symptomsSeen.set(assoc.symptom_id, symptom_name);

    if (!associationsBySymptom[assoc.symptom_id]) {
      associationsBySymptom[assoc.symptom_id] = [];
    }
    associationsBySymptom[assoc.symptom_id].push({
      symptom_id: assoc.symptom_id,
      ingredient_name: assoc.ingredient_name,
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

const DEFAULT_MIN_EXPOSURES = 3;

const initialState: AlgorithmState = {
  associationsBySymptom: {},
  symptoms: [],
  isLoading: false,
  error: null,
  minExposures: DEFAULT_MIN_EXPOSURES,
};

export const useAlgorithmStore = create<AlgorithmStore>((set) => ({
  ...initialState,

  fetchAssociations: async (userId: string) => {
    set({ isLoading: true, error: null });
    try {
      const [rawAssociations, symptomMap] = await Promise.all([
        algorithmService.getAssociations(userId),
        buildSymptomMap(),
      ]);

      const { associationsBySymptom, symptoms } = enrichAndGroup(rawAssociations, symptomMap);
      set({ associationsBySymptom, symptoms, isLoading: false });
    } catch (err: any) {
      set({ error: err.message ?? 'Failed to load associations', isLoading: false });
    }
  },

  setMinExposures: (minExposures: number) => {
    set({ minExposures: Math.max(1, minExposures) });
  },

  runAlgorithm: async (userId: string) => {
    set({ isLoading: true, error: null });
    try {
      const [rawAssociations, symptomMap] = await Promise.all([
        algorithmService.analyze({ user_id: userId, time_window_hours: 6.0 }),
        buildSymptomMap(),
      ]);

      const { associationsBySymptom, symptoms } = enrichAndGroup(rawAssociations.associations, symptomMap);
      set({ associationsBySymptom, symptoms, isLoading: false });
    } catch (err: any) {
      set({ error: err.message ?? 'Failed to run algorithm', isLoading: false });
    }
  },
}));
