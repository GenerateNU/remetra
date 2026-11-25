import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { WeeklyResultsScreen, resultsState } from '../WeeklyResultsScreen';
import { weeklyResultsService } from '../../../api/weekly_results_service';
import { ApiError } from '../../../api/client';
import { shortDate, weekdayDate, weeklyUpdateInfo } from '../../../utils/weeklyUpdate';
import { allStillLearning, empty, noClearPattern, withTrigger } from '../../../api/__fixtures__/weeklyResults';

jest.mock('expo-font', () => ({ useFonts: () => [true] }));
jest.mock('@expo-google-fonts/prata', () => ({ Prata_400Regular: 0 }));
jest.mock('@expo-google-fonts/figtree', () => ({ Figtree_400Regular: 0, Figtree_600SemiBold: 0 }));
jest.mock('../../../components/weekly/HaloBackground', () => ({ HaloBackground: () => null }));
jest.mock('../../../api/weekly_results_service', () => ({
  weeklyResultsService: { getWeekly: jest.fn() },
}));
const mockGoBack = jest.fn();
jest.mock('../../../navigation/hooks', () => ({
  useAppNavigation: () => ({ goBack: mockGoBack }),
}));

const mockGetWeekly = weeklyResultsService.getWeekly as jest.Mock;

beforeEach(() => jest.clearAllMocks());

async function renderWith(response: typeof withTrigger) {
  mockGetWeekly.mockResolvedValue(response);
  render(<WeeklyResultsScreen />);
  await waitFor(() => expect(screen.queryByTestId('weekly-results-loading')).toBeNull());
}

describe('resultsState', () => {
  it.each([
    [empty, 'empty'],
    [noClearPattern, 'no_clear_pattern'],
    [allStillLearning, 'results'],
    [withTrigger, 'results'],
  ])('picks the right state', (response, expected) => {
    expect(resultsState(response)).toBe(expected);
  });
});

describe('WeeklyResultsScreen', () => {
  it('shows a spinner while loading', () => {
    mockGetWeekly.mockReturnValue(new Promise(() => {}));

    render(<WeeklyResultsScreen />);

    expect(screen.getByTestId('weekly-results-loading')).toBeTruthy();
  });

  it('shows triggers first, then looks fine, then still learning (Figma order)', async () => {
    await renderWith(withTrigger);

    expect(screen.getByTestId('trigger-card-fructans_allium')).toBeTruthy();
    expect(screen.getByTestId('looks-fine-card')).toBeTruthy();
    expect(screen.getByTestId('still-learning-card')).toBeTruthy();
    expect(screen.queryByTestId('weekly-results-no_clear_pattern')).toBeNull();

    const tree = JSON.stringify(screen.toJSON());
    const order = ['Onion & garlic family', 'Looks fine for you', '2 food groups'].map((text) => tree.indexOf(text));
    expect(order.every((i) => i >= 0)).toBe(true);
    expect(order).toEqual([...order].sort((a, b) => a - b));
  });

  it('shows an always-together group once, by its group name', async () => {
    await renderWith(withTrigger);

    expect(screen.getAllByText('Wheat, rye & barley (gluten or wheat carbs)')).toHaveLength(1);
    expect(screen.queryByText(/^gluten$|^fructans_grain$/)).toBeNull();
  });

  it('never shows confidence numbers, only counts and dates', async () => {
    await renderWith(withTrigger);

    expect(screen.queryByText(/%|\d\.\d/)).toBeNull();
    const numbered = screen.getAllByText(/\d/).map((node) => [node.props.children].flat().join(''));
    expect(numbered).toEqual([
      expect.stringMatching(/^Week \d+ update, [A-Z][a-z]{2} \d{1,2}$/),
      'We’ve checked 3 of 31 food groups',
      expect.stringMatching(/^Next update Sunday, [A-Z][a-z]{2} \d{1,2}$/),
      '2 food groups',
    ]);
  });

  it('shows the progress card and the ask card', async () => {
    await renderWith(withTrigger);

    expect(screen.getByTestId('progress-card')).toBeTruthy();
    expect(screen.getByText('See insights')).toBeTruthy();
    expect(screen.getByTestId('ask-entry-card')).toBeTruthy();
  });

  it('labels the update by week, counted from the first meal', async () => {
    // The week math itself is tested in utils/__tests__/weeklyUpdate.test.ts
    const update = weeklyUpdateInfo(new Date(withTrigger.first_meal_at!));
    await renderWith(withTrigger);

    expect(screen.getByText(`Week ${update.week} update, ${shortDate(update.updateDate)}`)).toBeTruthy();
    expect(screen.getByText(`Next update ${weekdayDate(update.nextUpdateDate)}`)).toBeTruthy();
  });

  it('frames results as patterns, not a diagnosis', async () => {
    await renderWith(withTrigger);

    expect(screen.getByText('These are patterns in your logs, not a diagnosis.')).toBeTruthy();
  });

  it('shows the no clear pattern message', async () => {
    await renderWith(noClearPattern);

    expect(screen.getByTestId('weekly-results-no_clear_pattern')).toBeTruthy();
    expect(screen.getByText('No clear food pattern')).toBeTruthy();
    expect(screen.queryByText('Likely trigger')).toBeNull();
  });

  it('shows only the still learning card when nothing has a label yet', async () => {
    await renderWith(allStillLearning);

    expect(screen.getByText('2 food groups')).toBeTruthy();
    expect(screen.queryByTestId('section-looks_fine')).toBeNull();
    expect(screen.queryByTestId('section-likely_trigger')).toBeNull();
  });

  it('tells a new user their results are on the way', async () => {
    await renderWith(empty);

    expect(screen.getByTestId('weekly-results-empty')).toBeTruthy();
    expect(screen.queryByTestId('section-still_learning')).toBeNull();
    expect(screen.queryByTestId('progress-card')).toBeNull();
    expect(screen.getByText('Weekly update')).toBeTruthy();
    expect(screen.queryByText(/not a diagnosis/)).toBeNull();
  });

  it('shows the error and retries', async () => {
    mockGetWeekly.mockRejectedValueOnce(new ApiError('Failed to fetch weekly results'));
    mockGetWeekly.mockResolvedValueOnce(withTrigger);
    render(<WeeklyResultsScreen />);

    fireEvent.press(await screen.findByText('Try again'));

    expect(await screen.findByTestId('trigger-card-fructans_allium')).toBeTruthy();
    expect(mockGetWeekly).toHaveBeenCalledTimes(2);
  });

  it('goes back', async () => {
    await renderWith(empty);

    fireEvent.press(screen.getByText('Back'));

    expect(mockGoBack).toHaveBeenCalled();
  });
});
