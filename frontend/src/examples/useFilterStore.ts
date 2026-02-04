// This would be in src/store/useFilterStore.ts
import { create } from 'zustand';
import type { ChocolateFilters } from './chocolates';

interface FilterState extends ChocolateFilters {
  setMinPrice: (price: number | undefined) => void;
  setMaxPrice: (price: number | undefined) => void;
  setInStockOnly: (inStock: boolean) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  min_price: undefined,
  max_price: undefined,
  in_stock_only: false,
  setMinPrice: (price) => set({ min_price: price }),
  setMaxPrice: (price) => set({ max_price: price }),
  setInStockOnly: (inStock) => set({ in_stock_only: inStock }),
  clearFilters: () => set({ min_price: undefined, max_price: undefined, in_stock_only: false }),
}));