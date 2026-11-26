import { dinnerService, SAMPLE_DINNER } from "../dinner_service";
import { apiClient, ApiError } from "../client";

jest.mock('../client', () => ({
    ...jest.requireActual('../client'),
    apiClient: { get: jest.fn() },
}));

const mockGet = apiClient.get as jest.Mock;

beforeEach(() => {
    jest.clearAllMocks();
    dinnerService.useSampleData = true;
});

test('returns the sample dinner while sample data is on, without calling the API', async () => {
    await expect(dinnerService.getTonightsDinner()).resolves.toEqual(SAMPLE_DINNER);
    expect(mockGet).not.toHaveBeenCalled();
});

test('the sample dinner has ingredients and a recipe with a title and link', () => {
    expect(SAMPLE_DINNER.ingredients.length).toBeGreaterThan(0);
    expect(SAMPLE_DINNER.recipe.title).toBeTruthy();
    expect(SAMPLE_DINNER.recipe.source_url).toMatch(/^https:\/\//);
});

test('calls the dinner endpoint when sample data is off', async () => {
    dinnerService.useSampleData = false;
    mockGet.mockResolvedValue({ data: SAMPLE_DINNER });
    
    await expect(dinnerService.getTonightsDinner()).resolves.toEqual(SAMPLE_DINNER);
    expect(mockGet).toHaveBeenCalledWith('/dinner/tonight');
});

test('returns null when there is no dinner yet', async () => {
    dinnerService.useSampleData = false;
    mockGet.mockResolvedValue({ data: null });
    
    await expect(dinnerService.getTonightsDinner()).resolves.toBeNull();
});

test('errors carry the backend detail', async () => {
    dinnerService.useSampleData = false;
    mockGet.mockRejectedValue({ response: { data: { detail: 'Something went wrong' } } });
    
    await expect(dinnerService.getTonightsDinner()).rejects.toEqual(new ApiError('Something went wrong'));
});