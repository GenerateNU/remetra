import { apiClient, ApiError } from './client';

export interface MeResponse {
  username: string;
  email: string;
  dob?: string | null;
  disease?: string[] | null;
  weight?: number | null;
  gender?: string | null;
  medication?: string[] | null;
  created_at: string;
  updated_at?: string | null;
}

export interface UserUpdatePayload {
  dob?: string;
  gender?: string;
  weight?: number;
  disease?: string[];
  medication?: string[];
}

export const authService = {
  // GET /auth/me -> get_current_user()
  async getMe(): Promise<MeResponse> {
    try {
      const { data } = await apiClient.get('/auth/me');
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch user profile');
    }
  },

  // PUT /auth/me -> update_profile()
  async updateProfile(payload: UserUpdatePayload): Promise<MeResponse> {
    try {
      const { data } = await apiClient.put('/auth/me', payload);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to update profile');
    }
  },
};
