import { fireEvent, render, screen, within } from '@testing-library/react-native';
import { TriggerCard } from '../weekly/TriggerCard';
import { LooksFineCard } from '../weekly/LooksFineCard';
import { StillLearningCard } from '../weekly/StillLearningCard';
import { ProgressCard } from '../weekly/ProgressCard';
import { BloomRing } from '../weekly/BloomRing';
import { withTrigger } from '../../api/__fixtures__/weeklyResults';

describe('TriggerCard', () => {
  it('shows the food, the likely trigger tag, and pattern-not-diagnosis copy', () => {
    // Arrange / Act
    render(<TriggerCard item={withTrigger.likely_trigger[0]} />);

    // Assert
    expect(screen.getByText('Onion & garlic family')).toBeTruthy();
    expect(screen.getByText('Likely trigger')).toBeTruthy();
    expect(screen.getByText(/discussing it with your clinician or dietitian/)).toBeTruthy();
  });
});

describe('LooksFineCard', () => {
  it('shows one chip per food', () => {
    render(<LooksFineCard items={withTrigger.looks_fine} />);

    const card = screen.getByTestId('looks-fine-card');
    expect(within(card).getByText('Wheat, rye & barley (gluten or wheat carbs)')).toBeTruthy();
    expect(within(card).getByText('Egg')).toBeTruthy();
    expect(screen.getByTestId('looks-fine-wheat')).toBeTruthy();
  });
});

describe('StillLearningCard', () => {
  it.each([
    [1, '1 food group'],
    [3, '3 food groups'],
  ])('shows %i as "%s"', (count, text) => {
    render(<StillLearningCard count={count} />);

    expect(screen.getByText(text)).toBeTruthy();
    expect(screen.getByText('Still learning')).toBeTruthy();
  });
});

describe('ProgressCard', () => {
  it('shows the counts and next update, and links to the results', () => {
    const onSeeInsights = jest.fn();
    render(<ProgressCard checked={15} total={35} nextUpdate="Sunday, Oct 27" onSeeInsights={onSeeInsights} />);

    expect(screen.getByText('We’ve checked 15 of 35 food groups')).toBeTruthy();
    expect(screen.getByText('Next update Sunday, Oct 27')).toBeTruthy();
    fireEvent.press(screen.getByText('See insights'));
    expect(onSeeInsights).toHaveBeenCalled();
  });
});

describe('BloomRing', () => {
  it('draws no progress arc at zero', () => {
    render(<BloomRing progress={0} />);

    expect(screen.queryByTestId('bloom-ring-progress')).toBeNull();
  });

  it('draws the arc in proportion to progress', () => {
    render(<BloomRing progress={0.5} />);

    const [dash, gap] = String(screen.getByTestId('bloom-ring-progress').props.strokeDasharray)
      .split(/[ ,]+/)
      .map(Number);
    expect(dash / gap).toBeCloseTo(0.5);
  });
});
