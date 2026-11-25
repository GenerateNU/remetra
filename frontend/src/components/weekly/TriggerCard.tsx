import { View } from 'react-native';
import type { WeeklyLabelItem } from '../../api/weekly_results_service';
import SparkleTrigger from '../../assets/insights/sparkle-trigger.svg';
import { InsightBody, InsightTag, InsightTitle } from './InsightParts';

const TRIGGER_TEXT = '#78350f'; // remetra-trigger-text

/** Figma "Insight card", likely trigger. Amber, never red; framed as a pattern, not a diagnosis. */
export function TriggerCard({ item }: { item: WeeklyLabelItem }) {
  return (
    <View
      testID={`trigger-card-${item.id}`}
      className="w-full gap-3 rounded-[24px] border-[0.5px] border-remetra-trigger-line bg-remetra-trigger-bg p-5"
    >
      <InsightTag label="Likely trigger" color={TRIGGER_TEXT} Icon={SparkleTrigger} />
      <InsightTitle>{item.display_name}</InsightTitle>
      <InsightBody>
        You had symptoms after this more often than at other times, including a check meal. Consider discussing it
        with your clinician or dietitian.
      </InsightBody>
    </View>
  );
}
