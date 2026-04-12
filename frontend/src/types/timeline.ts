export type FoodTimelineEntry = {
  type: 'food';
  id: string;
  name: string;
  ingredients: string[];
  quantity: string | null;
  notes: string | null;
  timestamp: Date;
};

export type SymptomTimelineEntry = {
  type: 'symptom';
  id: string;
  name: string;
  location: string;
  sensation: string;
  intensity: number;
  duration: number | null;
  notes: string | null;
  timestamp: Date;
};

export type TimelineEntry = FoodTimelineEntry | SymptomTimelineEntry;
