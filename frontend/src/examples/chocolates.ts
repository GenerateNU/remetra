// src/types/chocolate.ts
export interface Chocolate {
  id: string;
  name: string;
  description: string;
  price: number;
  stock_quantity: number;
  cocoa_percentage: number | null;  // nullable, not optional
  created_at: string;
  updated_at: string;
}

export interface ChocolateFilters {
  min_price?: number;
  max_price?: number;
  in_stock_only?: boolean;
}