import { View } from 'react-native';
import SparkleLearning from '../../assets/insights/sparkle-learning.svg';
import { InsightBody, InsightTag, InsightTitle } from './InsightParts';

const SECONDARY_TEXT = '#6e5a50'; // remetra-text-secondary

/** Figma "Insight card", still learning: how many food groups need more meals. A count, never a confidence. */
export function StillLearningCard({ count }: { count: number }) {
  return (
    <View
      testID="still-learning-card"
      className="w-full gap-3 rounded-[24px] border-[0.5px] border-remetra-chip-line bg-remetra-sheet p-5"
    >
      <InsightTag label="Still learning" color={SECONDARY_TEXT} Icon={SparkleLearning} />
      <InsightTitle>{count === 1 ? '1 food group' : `${count} food groups`}</InsightTitle>
      <InsightBody>We need a few more clean, well-logged meals before we can say anything.</InsightBody>
    </View>
  );
}
