import { apiClient, ApiError } from './client';

export interface DinnerIngredient {
    id: string;
    name: string;
}

export interface Recipe {
    title: string;
    source_url: string;
}

export interface TonightsDinner {
    date: string;
    ingredients: DinnerIngredient[];
    recipe: Recipe;
}

export const SAMPLE_DINNER: TonightsDinner = {
    date: '2026-11-25',
    ingredients: [
        { id: 'sample-olive-oil', name: 'Olive oil' },
        { id: 'sample-sweet-potatoes', name: 'Sweet potatoes' },
        { id: 'sample-salt', name: 'Salt' },
        { id: 'sample-garlic-poweder', name: 'Garlic powder' },
        { id: 'sample-cinnamon', name: 'Cinnamon' },
    ],
    recipe: {
        title: 'Sweet Potato Fries',
        source_url: 'https://www.food.com/recipe/sweet-potato-fries-43469'
    },
};

export const dinnerService = {
    // Returns the sample data until the backend endpoint exists. Set to false so it calls the real API.
    useSampleData: true,

    // get_tonights_dinner()
    async getTonightsDinner(): Promise<TonightsDinner | null> {
        if (dinnerService.useSampleData) {
            return SAMPLE_DINNER;
        }
        try {
            const { data } = await apiClient.get<TonightsDinner | null>('/dinner/tonight');
            return data;
        } catch (err: any) {
            throw new ApiError(err.response?.data?.detail ?? "Failed to load tonight's dinner");
        }
    },
};