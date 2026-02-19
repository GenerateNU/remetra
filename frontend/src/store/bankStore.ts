
import { create } from "zustand";
import { FoodItem, SymptomItem } from "../types/logs";

interface BankStore {
  foods: FoodItem[];
  symptoms: SymptomItem[];
  fetchFoods: () => Promise<void>;
  fetchSymptoms: () => Promise<void>;
  addFood: (name: string, ingredients: string[]) => string;
  addSymptom: (name: string, location: string, sensation: string) => string;
  // removeFood: (id: string) => boolean;
  // removeSymptom: (id: string) => boolean;
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

  addFood: (name: string, ingredients: string[]) => {
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

  addSymptom: (name: string, location: string, sensation: string) => {
    const symptom = {
      name,
      location,
      sensation,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    };
    set((state) => ({ symptoms: [...state.symptoms, symptom] }));
    return symptom.id;
  },

  // removeFood: (id: string) => {

  // },
  // removeSymptom: (id: string) => {
    
  // }
}));