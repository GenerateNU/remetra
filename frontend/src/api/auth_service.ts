import { apiClient } from './client';

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  username: string;
}

export interface MeResponse {
  username: string;
  email: string;
}

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}


export const authService = {

  // POST /auth/signup -> register_user()
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    try {
      const { data } = await apiClient.post('/auth/signup', payload);
      return data;
    } catch (err: any) {
      throw new AuthError(err.response?.data?.detail ?? 'Registration failed');
    }
  },

  // POST /auth/login -> authenticate_user()
  async login(payload: LoginPayload): Promise<AuthResponse> {
    try {
      const { data } = await apiClient.post('/auth/login', payload);
      return data;
    } catch (err: any) {
      throw new AuthError(err.response?.data?.detail ?? 'Incorrect username or password');
    }
  },

  // GET /auth/me -> get_current_user()
  async getMe(): Promise<MeResponse> {
    try {
      const { data } = await apiClient.get('/auth/me');
      return data;
    } catch (err: any) {
      throw new AuthError(err.response?.data?.detail ?? 'Failed to fetch user profile');
    }
  },
};