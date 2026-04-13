
import { create } from "zustand";
import { FoodItem, SymptomItem } from "../types/logs";
import { foodService } from "../api/food_service";
import { symptomService } from "../api/symptom_service";

interface BankStore {
  foods: FoodItem[];
  symptoms: SymptomItem[];
  scannedFood: { name: string; ingredients: string[] } | null;
  fetchFoods: () => Promise<void>;
  fetchSymptoms: () => Promise<void>;
  addFood: (name: string, ingredients: string[]) => Promise<string | null>;
  addSymptom: (name: string, location: string, sensation: string) => Promise<string | null>;
  removeFood: (id: string) => Promise<boolean>;
  removeSymptom: (id: string) => Promise<boolean>;
  setScannedFood: (food: { name: string; ingredients: string[] } | null) => void;
  clearBank: () => void;
}

export const useBankStore = create<BankStore>((set, get) => ({
  foods: [],
  symptoms: [],
  scannedFood: null,
  setScannedFood: (food) => set({ scannedFood: food }),
  clearBank: () => set({ foods: [], symptoms: [], scannedFood: null }),

  fetchFoods: async () => {
    try {
      const data = await foodService.getAllFoods();
      const items: FoodItem[] = data.map((food) => ({
        id: food.id,
        name: food.name,
        ingredients: food.ingredients,
      }));
      set({ foods: items });
    } catch (err: any) {
      console.error("fetchFoods failed", err);
    }
  },

  fetchSymptoms: async () => {
    try {
      const data = await symptomService.getAllSymptoms();
      const items: SymptomItem[] = data.map((symptom) => ({
        id: symptom.id,
        name: symptom.name,
        location: symptom.location || "",
        sensation: symptom.sensation || "",
      }));
      set({ symptoms: items });
    } catch (err: any) {
      console.error("fetchSymptoms failed", err);
    }
  },

  addFood: async (name: string, ingredients: string[]) => {
    try {
      const response = await foodService.createFood({ name, ingredients });
      const food: FoodItem = {
        id: response.id,
        name: response.name,
        ingredients: response.ingredients,
      };
      set((state) => ({ foods: [...state.foods, food] }));
      return food.id;
    } catch (err: any) {
      console.error("addFood failed", err);
      return null;
    }
  },

  addSymptom: async (name: string, location: string, sensation: string) => {
    try {
      const response = await symptomService.createSymptom({ name, location, sensation });
      const symptom: SymptomItem = {
        id: response.id,
        name: response.name,
        location: response.location || "",
        sensation: response.sensation || "",
      };
      set((state) => ({ symptoms: [...state.symptoms, symptom] }));
      return symptom.id;
    } catch (err: any) {
      console.error("addSymptom failed", err);
      return null;
    }
  },

  removeFood: async (id: string) => {
    const exists = get().foods.some((f) => f.id === id);
    if (!exists) return false;

    try {
      await foodService.deleteFood(id);
      set((state) => ({ foods: state.foods.filter((f) => f.id !== id) }));
      return true;
    } catch (err: any) {
      console.error("removeFood failed", err);
      return false;
    }
  },

  removeSymptom: async (id: string) => {
    const exists = get().symptoms.some((s) => s.id === id);
    if (!exists) return false;

    try {
      await symptomService.deleteSymptom(id);
      set((state) => ({ symptoms: state.symptoms.filter((s) => s.id !== id) }));
      return true;
    } catch (err: any) {
      console.error("removeSymptom failed", err);
      return false;
    }
  },
}));