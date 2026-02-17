
import { create } from "zustand";
import { FoodItem, SymptomItem } from "../types/logs";

interface BankStore {
  foods: FoodItem[];
  symptoms: SymptomItem[];
  fetchFoods: () => Promise<void>;
  fetchSymptoms: () => Promise<void>;
  addCustomFood: (name: string, ingredients: string[]) => string;
  addCustomSymptom: (symptom: SymptomItem) => void;
}

export const useBankStore = create<BankStore>((set) => ({
  foods: [],
  symptoms: [],

  fetchFoods: async () => {
    // leave blank for now (replace with api call)
  },

  fetchSymptoms: async () => {
    // leave blank for now (replace with api call)
  },

  addCustomFood: (name: string, ingredients: string[]) => {
    const food = {
      name: name,
      ingredients: ingredients,
      // In the future we will probably let the backend make the UUID and return it from the response instead
      // Just use the current date as a placeholder
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
    }
    set((state) => ({ foods: [...state.foods, food] }))
    return food.id
  },

  addCustomSymptom: (symptom) =>
    set((state) => ({ symptoms: [...state.symptoms, symptom] })),
}));