import { apiClient } from './client';

export interface RegisterPayload {
  username: string;
  // email: string;
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

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}


export const authService = {

  // POST /auth/signup -> register_user()
  async register(payload: RegisterPayload): Promise<void> {
    try {
      await apiClient.post('/auth/signup', payload);
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
};