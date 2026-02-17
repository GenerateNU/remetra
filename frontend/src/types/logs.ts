export interface FoodItem {
  id: string;
  name: string;
  ingredients: string[];
}

export interface SymptomItem {
  id: string;
  name: string;
  location: string;
  sensation: string;
}

export interface FoodLogEntry {
  type: "food";
  foodId: string;
  name: string;
  ingredients: string[];
  servings: number;
  timestamp: Date;
}

export interface SymptomLogEntry {
  type: "symptom";
  symptomId: string;
  name: string;
  location: string;
  sensation: string;
  intensity: number; // 1-10
  timestamp: Date;
  durationMinutes: number | null;
}

export type LogEntry = FoodLogEntry | SymptomLogEntry;

type LogType = "food" | "symptom";
type ModalStep = "select_type" | "food" | "symptom";