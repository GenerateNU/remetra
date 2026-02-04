import { useState, useCallback } from 'react';
import { api } from './exampleApi';
import type { Chocolate, ChocolateFilters } from './chocolates';

export function useChocolates() {
  const [chocolates, setChocolates] = useState<Chocolate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChocolates = useCallback(async (filters?: ChocolateFilters) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getChocolates(filters);
      setChocolates(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch chocolates';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { chocolates, isLoading, error, fetchChocolates, clearError };
}