import { useFilterStore } from '../useFilterStore';

describe('useFilterStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    useFilterStore.setState({
      min_price: undefined,
      max_price: undefined,
      in_stock_only: false,
    });
  });

  it('initializes with default values', () => {
    const state = useFilterStore.getState();

    expect(state.min_price).toBeUndefined();
    expect(state.max_price).toBeUndefined();
    expect(state.in_stock_only).toBe(false);
  });

  it('sets min price', () => {
    useFilterStore.getState().setMinPrice(10);

    expect(useFilterStore.getState().min_price).toBe(10);
  });

  it('sets max price', () => {
    useFilterStore.getState().setMaxPrice(50);

    expect(useFilterStore.getState().max_price).toBe(50);
  });

  it('sets in stock only', () => {
    useFilterStore.getState().setInStockOnly(true);

    expect(useFilterStore.getState().in_stock_only).toBe(true);
  });

  it('clears all filters', () => {
    // Arrange
    const store = useFilterStore.getState();
    store.setMinPrice(10);
    store.setMaxPrice(50);
    store.setInStockOnly(true);

    // Act
    useFilterStore.getState().clearFilters();

    // Assert
    const state = useFilterStore.getState();
    expect(state.min_price).toBeUndefined();
    expect(state.max_price).toBeUndefined();
    expect(state.in_stock_only).toBe(false);
  });
});