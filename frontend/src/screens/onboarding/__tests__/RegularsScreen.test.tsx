import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { RegularsScreen } from '../RegularsScreen';
import { authService } from '../../../api/auth_service';
import { ApiError } from '../../../api/client';
import { ingredientService } from '../../../api/ingredient_service';
import { useAuthStore } from '../../../store/useAuthStore';
import { useOnboardingStore } from '../../../store/onboardingStore';

jest.mock('../OnboardingChrome', () => {
  const React = jest.requireActual('react');
  const { Pressable: Button, Text: Label, View: Box } = jest.requireActual('react-native');
  return {
    OnboardingChrome: ({
      children,
      onPrimary,
      onSkip,
      primaryLabel,
    }: {
      children: React.ReactNode;
      onPrimary: () => void;
      onSkip: () => void;
      primaryLabel: string;
    }) =>
      React.createElement(
        Box,
        null,
        children,
        React.createElement(Button, { onPress: onPrimary }, React.createElement(Label, null, primaryLabel)),
        React.createElement(Button, { onPress: onSkip }, React.createElement(Label, null, 'Skip for now'))
      ),
    ChoiceChip: ({ label, onPress }: { label: string; onPress: () => void }) =>
      React.createElement(Button, { onPress }, React.createElement(Label, null, label)),
  };
});
jest.mock('../../../navigation/hooks', () => ({
  useAppNavigation: () => ({ goBack: jest.fn() }),
}));
jest.mock('../../../api/auth_service', () => ({
  authService: { updateProfile: jest.fn(), getMe: jest.fn() },
}));
jest.mock('../../../api/ingredient_service', () => ({
  ingredientService: { replaceLabels: jest.fn() },
}));
jest.mock('../../../auth/clerkSession', () => ({
  clerkSignIn: jest.fn(),
  clerkSignUp: jest.fn(),
  clerkSignOut: jest.fn(),
}));

const mockUpdateProfile = authService.updateProfile as jest.Mock;
const mockReplaceLabels = ingredientService.replaceLabels as jest.Mock;

const emptyAnswers = { avoid: [], suspect: [], safe: [] };

describe('RegularsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useOnboardingStore.getState().reset();
    useAuthStore.getState().clearLocal();
    mockReplaceLabels.mockResolvedValue(undefined);
    mockUpdateProfile.mockResolvedValue({
      username: 'testuser',
      email: 'testuser@example.com',
      disease: [],
      created_at: '2026-01-01T00:00:00Z',
    });
  });

  it('saves food labels and an empty disease list when every answer was skipped', async () => {
    useOnboardingStore.setState({ conditions: ['None or prefer not to say'] });
    render(<RegularsScreen />);

    fireEvent.press(screen.getByText('Skip for now'));

    await waitFor(() => expect(useAuthStore.getState().hasCompletedOnboarding).toBe(true));
    expect(mockReplaceLabels).toHaveBeenCalledWith(emptyAnswers);
    expect(mockUpdateProfile).toHaveBeenCalledWith({ disease: [] });
  });

  it('saves the selected answers, including gluten for celiac, then finishes', async () => {
    useOnboardingStore.setState({
      conditions: ['Celiac disease'],
      exclusions: [{ name: 'Dairy', allergic: true }],
      suspicions: ['Coffee'],
      regulars: ['Eggs', 'Dairy'],
    });
    mockUpdateProfile.mockResolvedValue({
      username: 'testuser',
      email: 'testuser@example.com',
      disease: ['Celiac disease'],
      created_at: '2026-01-01T00:00:00Z',
    });

    render(<RegularsScreen />);
    fireEvent.press(screen.getByText('See tonight’s dinner'));

    await waitFor(() => expect(useAuthStore.getState().hasCompletedOnboarding).toBe(true));
    expect(mockReplaceLabels).toHaveBeenCalledWith({
      avoid: ['Dairy', 'Gluten'],
      suspect: ['Coffee'],
      safe: ['Eggs', 'Dairy'],
    });
    expect(mockUpdateProfile).toHaveBeenCalledWith({ disease: ['Celiac disease'] });
    expect(useAuthStore.getState().user.disease).toEqual(['Celiac disease']);
  });

  it('stays on the screen when saving food preferences fails', async () => {
    mockReplaceLabels.mockRejectedValue(new ApiError('Failed to save food preferences'));

    render(<RegularsScreen />);
    fireEvent.press(screen.getByText('See tonight’s dinner'));

    expect(await screen.findByText('Failed to save food preferences')).toBeTruthy();
    expect(mockUpdateProfile).not.toHaveBeenCalled();
    expect(useAuthStore.getState().hasCompletedOnboarding).toBe(false);
  });

  it('stays on the screen when the profile update fails', async () => {
    mockUpdateProfile.mockRejectedValue(new ApiError('Failed to update profile'));

    render(<RegularsScreen />);
    fireEvent.press(screen.getByText('Skip for now'));

    expect(await screen.findByText('Failed to update profile')).toBeTruthy();
    expect(mockReplaceLabels).toHaveBeenCalledWith(emptyAnswers);
    expect(useAuthStore.getState().hasCompletedOnboarding).toBe(false);
  });
});
