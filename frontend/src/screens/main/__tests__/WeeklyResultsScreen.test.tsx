import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { WeeklyResultsScreen, WeeklyResultsView } from '../WeeklyResultsScreen';
import { resultsService } from '../../../api/results_service';
import { ApiError } from '../../../api/client';
import type { WeeklyLabel, WeeklyLabelItem, WeeklyResultsResponse } from '../../../types/weeklyResults';

jest.mock('../../../api/results_service', () => ({ resultsService: { getWeeklyResults: jest.fn() } }));
jest.mock('expo-font', () => ({ useFonts: () => [true] }));
jest.mock('@expo-google-fonts/prata', () => ({ Prata_400Regular: 0 }));
jest.mock('@expo-google-fonts/figtree', () => ({ Figtree_400Regular: 0, Figtree_600SemiBold: 0 }));
jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

const item = (id: string, label: WeeklyLabel, members?: string[]): WeeklyLabelItem => ({
  id,
  display_name: id.replace('_', ' '),
  is_group: Boolean(members),
  member_slugs: members ?? [id],
  label,
});

const TRIGGER_FOUND: WeeklyResultsResponse = {
  likely_trigger: [item('onion', 'likely_trigger')],
  still_learning: [item('dairy', 'still_learning', ['lactose', 'milk_protein'])],
  looks_fine: [item('egg', 'looks_fine')],
  no_clear_pattern: false,
};
const NO_CLEAR_PATTERN: WeeklyResultsResponse = {
  likely_trigger: [],
  still_learning: [],
  looks_fine: [item('egg', 'looks_fine'), item('dairy', 'looks_fine', ['lactose', 'milk_protein'])],
  no_clear_pattern: true,
};
const STILL_LEARNING: WeeklyResultsResponse = {
  likely_trigger: [],
  still_learning: [item('onion', 'still_learning')],
  looks_fine: [],
  no_clear_pattern: false,
};
const EMPTY: WeeklyResultsResponse = { likely_trigger: [], still_learning: [], looks_fine: [], no_clear_pattern: false };

type Node = ReturnType<typeof screen.UNSAFE_root.findAll>[number];

/** Every string rendered on screen, so tests can check nothing numeric leaks through. */
function allText(): string {
  return screen
    .UNSAFE_root.findAll((node: Node) => typeof node.props.children === 'string')
    .map((node: Node) => node.props.children as string)
    .join(' ');
}

describe('WeeklyResultsView', () => {
  it('shows a planted trigger above still learning and looks fine', () => {
    // Arrange / Act
    render(<WeeklyResultsView results={TRIGGER_FOUND} />);

    // Assert
    expect(screen.getByTestId('likely-trigger-onion')).toBeTruthy();
    expect(screen.getByTestId('label-list-still_learning')).toBeTruthy();
    expect(screen.getByTestId('label-list-looks_fine')).toBeTruthy();
    expect(screen.queryByTestId('no-clear-pattern')).toBeNull();
  });

  it('shows the no clear pattern state', () => {
    render(<WeeklyResultsView results={NO_CLEAR_PATTERN} />);

    expect(screen.getByTestId('no-clear-pattern')).toBeTruthy();
    expect(screen.queryByText('Likely trigger')).toBeNull();
  });

  it('shows still learning foods when nothing has settled', () => {
    render(<WeeklyResultsView results={STILL_LEARNING} />);

    expect(screen.getByTestId('label-list-still_learning')).toBeTruthy();
    expect(screen.queryByTestId('label-list-looks_fine')).toBeNull();
  });

  it('shows the empty still learning state when no food is labelled', () => {
    render(<WeeklyResultsView results={EMPTY} />);

    expect(screen.getByTestId('still-learning-empty')).toBeTruthy();
  });

  it.each([TRIGGER_FOUND, NO_CLEAR_PATTERN, STILL_LEARNING, EMPTY])(
    'never shows numbers or percentages',
    (results) => {
      render(<WeeklyResultsView results={results} />);

      expect(allText()).not.toMatch(/\d|%/);
    },
  );

  it('shows the empty still learning state when no results are passed', () => {
    render(<WeeklyResultsView />);

    expect(screen.getByTestId('still-learning-empty')).toBeTruthy();
  });

  it('shows loading and error states', () => {
    const { rerender } = render(<WeeklyResultsView isLoading />);
    expect(screen.getByTestId('weekly-results-loading')).toBeTruthy();

    rerender(<WeeklyResultsView error="Could not load your results" />);
    expect(screen.getByText('Could not load your results')).toBeTruthy();
  });

  it('calls onBack when back is pressed', () => {
    const onBack = jest.fn();
    render(<WeeklyResultsView onBack={onBack} />);

    fireEvent.press(screen.getByLabelText('Back'));

    expect(onBack).toHaveBeenCalledTimes(1);
  });
});

describe('WeeklyResultsScreen', () => {
  const mockGet = resultsService.getWeeklyResults as jest.Mock;

  beforeEach(() => jest.clearAllMocks());

  it('loads the weekly results from the API', async () => {
    // Arrange
    mockGet.mockResolvedValue(TRIGGER_FOUND);

    // Act
    render(<WeeklyResultsScreen />);

    // Assert
    expect(screen.getByTestId('weekly-results-loading')).toBeTruthy();
    expect(await screen.findByTestId('likely-trigger-onion')).toBeTruthy();
    expect(mockGet).toHaveBeenCalledTimes(1);
  });

  it('shows the error and retries', async () => {
    // Arrange
    mockGet.mockRejectedValueOnce(new ApiError('Failed to fetch weekly results')).mockResolvedValueOnce(EMPTY);
    render(<WeeklyResultsScreen />);
    expect(await screen.findByText('Failed to fetch weekly results')).toBeTruthy();

    // Act
    fireEvent.press(screen.getByText('Try again'));

    // Assert
    await waitFor(() => expect(screen.getByTestId('still-learning-empty')).toBeTruthy());
    expect(mockGet).toHaveBeenCalledTimes(2);
  });
});
