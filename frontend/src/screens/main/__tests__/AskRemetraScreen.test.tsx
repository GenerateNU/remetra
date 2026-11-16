import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { Linking } from 'react-native';
import { AskRemetraScreen } from '../AskRemetraScreen';
import { useAuthStore } from '../../../store/useAuthStore';
import type { AskEntry } from '../../../types/chat';

const mockGoBack = jest.fn();
let mockEntry: AskEntry | undefined;

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useRoute: () => ({ params: mockEntry ? { entry: mockEntry } : undefined }),
}));
jest.mock('../../../navigation/hooks', () => ({ useAppNavigation: () => ({ goBack: mockGoBack }) }));
jest.mock('react-native-safe-area-context', () => jest.requireActual('react-native-safe-area-context/jest/mock').default);
jest.mock('../../../components/ask/useAskFonts', () => ({ useAskFonts: () => true }));
jest.mock('../../../components/LogEntryModal', () => () => null);
jest.mock('../../../auth/clerkSession', () => ({
  clerkSignIn: jest.fn(),
  clerkSignUp: jest.fn(),
  clerkSignOut: jest.fn(),
}));
jest.mock('../../../api/chat_service', () => {
  const { createMockChatEngine } = jest.requireActual('../../../api/mock_chat_engine');
  return {
    CHAT_USES_MOCK: true,
    chatService: {
      createSession: () => {
        const engine = createMockChatEngine();
        return { send: async (message: string) => engine.reply(message) };
      },
    },
  };
});

describe('AskRemetraScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockEntry = undefined;
    useAuthStore.setState((state) => ({ user: { ...state.user, name: 'Nicole' } }));
  });

  it('shows the start state with the greeting and starters (screen 01)', () => {
    render(<AskRemetraScreen />);

    expect(screen.getByText('Hi Nicole, what would help today?')).toBeTruthy();
    expect(screen.getByText('Understand my insights')).toBeTruthy();
    expect(screen.getByText('Log by chatting')).toBeTruthy();
    expect(screen.getByPlaceholderText('Ask about your symptoms or meals')).toBeTruthy();
  });

  it('sends a starter with its context chip and renders the reply card (screen 02)', async () => {
    render(<AskRemetraScreen />);

    fireEvent.press(screen.getByText('Understand my insights'));

    expect(await screen.findByText('Onion & garlic family')).toBeTruthy();
    expect(screen.getByText('From your week 3 update')).toBeTruthy();
    expect(screen.getByText('Why is onion & garlic a likely trigger?')).toBeTruthy();
    expect(screen.getByText('What can I do next?')).toBeTruthy();
  });

  it('sends typed messages from the composer and shows the safety banner (screen 11)', async () => {
    const openURL = jest.spyOn(Linking, 'openURL').mockResolvedValue(undefined);
    render(<AskRemetraScreen />);

    fireEvent.changeText(screen.getByLabelText('Message Remetra'), 'My lips are swelling after lunch');
    fireEvent.press(screen.getByLabelText('Send'));

    fireEvent.press(await screen.findByText('Call emergency services'));
    expect(openURL).toHaveBeenCalledWith('tel:911');
  });

  it('uses the log placeholder and context chip from the Log tab entry', async () => {
    mockEntry = 'log';
    render(<AskRemetraScreen />);

    fireEvent.changeText(
      screen.getByPlaceholderText('Tell me what you ate or how you feel'),
      'I had a turkey sandwich around 1'
    );
    fireEvent.press(screen.getByLabelText('Send'));

    expect(await screen.findByText('From today’s log')).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByText(/Was it on gluten-free bread\?/)).toBeTruthy();
    });
  });

  it('renders every reply card from the designs (screens 03–10)', async () => {
    render(<AskRemetraScreen />);
    const ask = async (message: string, expected: string | RegExp) => {
      fireEvent.changeText(screen.getByLabelText('Message Remetra'), message);
      fireEvent.press(screen.getByLabelText('Send'));
      expect(await screen.findByText(expected)).toBeTruthy();
    };

    await ask('Have my symptoms improved?', 'Your last 4 weeks · Sep 30 to Oct 26');
    await ask('I only have 20 minutes', 'Lemon herb salmon, 20-minute version');
    fireEvent.press(screen.getByText('Use this version'));
    expect(screen.queryByText('Keep original')).toBeNull();
    await ask('What could I order at a Thai place?', 'Good options to ask about');
    await ask('I had a turkey sandwich around 1', /Was it on gluten-free bread\?/);
    await ask('Yes, gluten-free bread', 'Draft food entry');
    await ask('Felt bloated after lunch, maybe a 4', /About what time did it start\?/);
    await ask('Around 2 PM', 'Symptom entry');
    await ask('Summarize my last month for my dietitian', 'Sep 30 to Oct 24');
    await ask('Add shrimp to tonight’s dinner', 'Add a soft-boiled egg');
    await ask('Is spicy food my trigger?', 'Sunday morning');
    await ask('How likely is it that garlic is the problem?', /I don’t share percentages/);
  });

  it('opens straight into the weekly update (screen 12)', () => {
    mockEntry = 'weekly_update';
    render(<AskRemetraScreen />);

    expect(screen.getByText('One new likely trigger and six groups that look fine')).toBeTruthy();
    expect(screen.getByText('Likely trigger · 1')).toBeTruthy();
    expect(screen.getByText('Walk me through it')).toBeTruthy();
  });

  it('goes back from the top bar', () => {
    render(<AskRemetraScreen />);

    fireEvent.press(screen.getByLabelText('Back'));

    expect(mockGoBack).toHaveBeenCalled();
  });
});
