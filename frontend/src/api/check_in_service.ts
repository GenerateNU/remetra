import { apiClient, ApiError } from './client';

export interface NoSymptomsCheckInPayload {
    date: string;
    timezone: string;
}

export interface CheckInResponse {
    id: string;
    username: string;
    date: string;
    timezone: string;
    created_at: string;
}

export const checkInService = {

    // check_in_no_symptoms()
    async checkInNoSymptoms(payload: NoSymptomsCheckInPayload): Promise<CheckInResponse> {
        try {
            const { data } = await apiClient.post<CheckInResponse>('/check-ins/no_symptoms', payload);
            return data;
        } catch (err: any) {
          throw new ApiError(err.response?.data?.detail ?? 'Failed to record check-in');
        }
    },
};