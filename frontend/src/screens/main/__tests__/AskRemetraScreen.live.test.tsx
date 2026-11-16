import { fireEvent, render, screen } from '@testing-library/react-native';
import { AskRemetraScreen } from '../AskRemetraScreen';
import { apiClient } from '../../../api/client';
import { useAuthStore } from '../../../store/useAuthStore';

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useRoute: () => ({ params: { entry: 'insights' } }),
}));
jest.mock('../../../navigation/hooks', () => ({ useAppNavigation: () => ({ goBack: jest.fn() }) }));
jest.mock('react-native-safe-area-context', () => jest.requireActual('react-native-safe-area-context/jest/mock').default);
jest.mock('../../../components/ask/useAskFonts', () => ({ useAskFonts: () => true }));
jest.mock('../../../components/LogEntryModal', () => () => null);
jest.mock('../../../auth/clerkSession', () => ({
  clerkSignIn: jest.fn(),
  clerkSignUp: jest.fn(),
  clerkSignOut: jest.fn(),
}));
jest.mock('../../../api/client', () => ({
  ...jest.requireActual('../../../api/client'),
  apiClient: { post: jest.fn() },
}));

const mockPost = apiClient.post as jest.Mock;

describe('AskRemetraScreen with the live chatbot', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState((state) => ({ user: { ...state.user, name: 'Nicole' } }));
  });

  it('offers starters the backend can answer instead of the demo flows', () => {
    render(<AskRemetraScreen />);

    expect(screen.getByText('What do my logs show about triggers so far?')).toBeTruthy();
    expect(screen.getByText('Check my logging')).toBeTruthy();
    expect(screen.queryByText('I had a turkey sandwich around 1')).toBeNull();
    expect(screen.queryByText('What could I order at a Thai place?')).toBeNull();
  });

  it('sends a starter to POST /chat and shows the answer', async () => {
    mockPost.mockResolvedValue({
      data: { answer: 'Okay so, your logs don’t show any triggers yet. Keep logging, you’ve got this.', kind: 'answer' },
    });
    render(<AskRemetraScreen />);

    fireEvent.press(screen.getByText('Understand my insights'));

    expect(await screen.findByText(/your logs don’t show any triggers yet/)).toBeTruthy();
    expect(screen.getByText('From your insights')).toBeTruthy();
    expect(mockPost).toHaveBeenCalledWith(
      '/chat',
      { question: 'What do my logs show about triggers so far?' },
      expect.anything()
    );
  });

  it('shows a readable message when the chatbot is unavailable', async () => {
    mockPost.mockRejectedValue({ response: { status: 502 } });
    render(<AskRemetraScreen />);

    fireEvent.changeText(screen.getByLabelText('Message Remetra'), 'Have my symptoms improved?');
    fireEvent.press(screen.getByLabelText('Send'));

    expect(await screen.findByText('Sorry, I couldn’t answer just now. Please try again in a moment.')).toBeTruthy();
  });
});
