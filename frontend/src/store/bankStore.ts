
import { create } from "zustand";
import { FoodItem, SymptomItem } from "../types/logs";

interface BankStore {
  foods: FoodItem[];
  symptoms: SymptomItem[];
  fetchFoods: () => Promise<void>;
  fetchSymptoms: () => Promise<void>;
  addCustomFood: (food: FoodItem) => void;
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

  addCustomFood: (food) =>
    set((state) => ({ foods: [...state.foods, food] })),

  addCustomSymptom: (symptom) =>
    set((state) => ({ symptoms: [...state.symptoms, symptom] })),
}));