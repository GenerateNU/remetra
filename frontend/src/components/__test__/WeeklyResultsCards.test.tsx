import { render, screen } from '@testing-library/react-native';
import {
  LabelListCard,
  LikelyTriggerCard,
  NoClearPatternCard,
  StillLearningEmptyCard,
} from '../results/WeeklyResultsCards';
import type { WeeklyLabelItem } from '../../types/weeklyResults';

const onion: WeeklyLabelItem = {
  id: 'fructans_allium',
  display_name: 'Onion & garlic',
  is_group: false,
  member_slugs: ['fructans_allium'],
  label: 'likely_trigger',
};
const wheat: WeeklyLabelItem = {
  id: 'wheat',
  display_name: 'Wheat, rye & barley (gluten or wheat carbs)',
  is_group: true,
  member_slugs: ['gluten', 'fructans_grain'],
  label: 'looks_fine',
};
const egg: WeeklyLabelItem = { id: 'egg_protein', display_name: 'Egg', is_group: false, member_slugs: ['egg_protein'], label: 'looks_fine' };

describe('LikelyTriggerCard', () => {
  it('shows the label and food name', () => {
    // Arrange / Act
    render(<LikelyTriggerCard item={onion} />);

    // Assert
    expect(screen.getByText('Likely trigger')).toBeTruthy();
    expect(screen.getByText('Onion & garlic')).toBeTruthy();
    expect(screen.queryByText(/checked as one/)).toBeNull();
  });

  it('explains always-together groups', () => {
    render(<LikelyTriggerCard item={{ ...wheat, label: 'likely_trigger' }} />);

    expect(screen.getByText(/checked as one/)).toBeTruthy();
  });
});

describe('LabelListCard', () => {
  it('lists every food under the label, groups as one row', () => {
    // Arrange / Act
    render(<LabelListCard label="looks_fine" items={[egg, wheat]} />);

    // Assert
    expect(screen.getByText('Looks fine')).toBeTruthy();
    expect(screen.getByTestId('food-row-egg_protein')).toBeTruthy();
    expect(screen.getByTestId('food-row-wheat')).toBeTruthy();
    expect(screen.queryByTestId('food-row-gluten')).toBeNull();
    expect(screen.getAllByText(/checked as one/)).toHaveLength(1);
  });

  it('uses still learning copy', () => {
    render(<LabelListCard label="still_learning" items={[egg]} />);

    expect(screen.getByText('Still learning')).toBeTruthy();
    expect(screen.getByText(/Not enough yet/)).toBeTruthy();
  });

  it('renders nothing when there are no foods', () => {
    render(<LabelListCard label="looks_fine" items={[]} />);

    expect(screen.queryByTestId('label-list-looks_fine')).toBeNull();
  });
});

describe('state cards', () => {
  it('NoClearPatternCard shows the no-pattern state', () => {
    render(<NoClearPatternCard />);

    expect(screen.getByText('No clear food pattern')).toBeTruthy();
  });

  it('StillLearningEmptyCard shows the empty state', () => {
    render(<StillLearningEmptyCard />);

    expect(screen.getByText('Still learning')).toBeTruthy();
    expect(screen.getByText('Your first results are on the way')).toBeTruthy();
  });
});
