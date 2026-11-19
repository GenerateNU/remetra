import type { FoodLogResponse } from '../api/food_log_service';
import type { SymptomLogResponse } from '../api/symptom_log_service';
import type { FoodItem, SymptomItem } from '../types/logs';
import type { FoodTimelineEntry, SymptomTimelineEntry, TimelineEntry } from '../types/timeline';

/** Joins logs with the user's food and symptom banks into card entries, oldest first. */
export function toTimelineEntries(
  foodLogs: FoodLogResponse[],
  symptomLogs: SymptomLogResponse[],
  foods: FoodItem[],
  symptoms: SymptomItem[],
): TimelineEntry[] {
  const foodMap = new Map(foods.map((f) => [f.id, f]));
  const symptomMap = new Map(symptoms.map((s) => [s.id, s]));

  const foodEntries: FoodTimelineEntry[] = foodLogs.map((log) => {
    const food = foodMap.get(log.food_id);
    return {
      type: 'food',
      id: log.id,
      name: food?.name ?? 'Unknown Food',
      ingredients: food?.ingredients ?? [],
      quantity: log.quantity,
      notes: log.notes,
      timestamp: new Date(log.timestamp),
    };
  });

  const symptomEntries: SymptomTimelineEntry[] = symptomLogs.map((log) => {
    const symptom = symptomMap.get(log.symptom_id);
    return {
      type: 'symptom',
      id: log.id,
      name: symptom?.name ?? 'Unknown Symptom',
      location: symptom?.location ?? '',
      sensation: symptom?.sensation ?? '',
      intensity: log.intensity,
      duration: log.duration,
      notes: log.notes,
      timestamp: new Date(log.timestamp),
    };
  });

  return [...foodEntries, ...symptomEntries].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
}
