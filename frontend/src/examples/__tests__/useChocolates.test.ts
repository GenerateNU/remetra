import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useChocolates } from '../useChocolates';
import { api } from '../exampleApi';

jest.mock('../exampleApi');
const mockApi = api as jest.Mocked<typeof api>;

const mockChocolates = [
  {
    id: '1',
    name: 'Dark Truffle',
    description: '70% cocoa dark chocolate',
    price: 5.99,
    stock_quantity: 50,
    cocoa_percentage: 70,
    created_at: '2024-01-15T12:00:00Z',
    updated_at: '2024-01-15T12:00:00Z',
  },
  {
    id: '2',
    name: 'Milk Hazelnut',
    description: 'Creamy milk chocolate with hazelnut center',
    price: 4.99,
    stock_quantity: 0,
    cocoa_percentage: 35,
    created_at: '2024-01-15T12:00:00Z',
    updated_at: '2024-01-15T12:00:00Z',
  },
];

describe('useChocolates', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useChocolates());

    expect(result.current.chocolates).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('fetches chocolates successfully', async () => {
    // Arrange
    mockApi.getChocolates.mockResolvedValueOnce(mockChocolates);

    // Act
    const { result } = renderHook(() => useChocolates());
    act(() => {
      result.current.fetchChocolates();
    });

    // Assert - loading state
    expect(result.current.isLoading).toBe(true);

    // Assert - success state
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.chocolates).toEqual(mockChocolates);
    expect(result.current.error).toBeNull();
    expect(mockApi.getChocolates).toHaveBeenCalledTimes(1);
  });

  it('passes filters to the API', async () => {
    // Arrange
    mockApi.getChocolates.mockResolvedValueOnce([mockChocolates[0]]);
    const filters = { min_price: 5, in_stock_only: true };

    // Act
    const { result } = renderHook(() => useChocolates());
    act(() => {
      result.current.fetchChocolates(filters);
    });

    // Assert
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockApi.getChocolates).toHaveBeenCalledWith(filters);
  });

  it('handles fetch error', async () => {
    // Arrange
    mockApi.getChocolates.mockRejectedValueOnce(new Error('Network error'));

    // Act
    const { result } = renderHook(() => useChocolates());
    act(() => {
      result.current.fetchChocolates();
    });

    // Assert
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.chocolates).toEqual([]);
  });

  it('handles non-Error rejection', async () => {
    // Arrange
    mockApi.getChocolates.mockRejectedValueOnce('Unknown failure');

    // Act
    const { result } = renderHook(() => useChocolates());
    act(() => {
      result.current.fetchChocolates();
    });

    // Assert
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to fetch chocolates');
  });

  it('clears error when clearError is called', async () => {
    // Arrange
    mockApi.getChocolates.mockRejectedValueOnce(new Error('Network error'));
    const { result } = renderHook(() => useChocolates());

    // Act - trigger error
    act(() => {
      result.current.fetchChocolates();
    });
    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });

    // Act - clear error
    act(() => {
      result.current.clearError();
    });

    // Assert
    expect(result.current.error).toBeNull();
  });

  it('clears previous error on new fetch', async () => {
    // Arrange - first call fails
    mockApi.getChocolates.mockRejectedValueOnce(new Error('Network error'));
    const { result } = renderHook(() => useChocolates());

    act(() => {
      result.current.fetchChocolates();
    });
    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });

    // Arrange - second call succeeds
    mockApi.getChocolates.mockResolvedValueOnce(mockChocolates);

    // Act
    act(() => {
      result.current.fetchChocolates();
    });

    // Assert - error cleared during loading
    expect(result.current.error).toBeNull();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.chocolates).toEqual(mockChocolates);
  });
});