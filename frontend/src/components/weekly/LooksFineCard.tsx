import { Text, View } from 'react-native';
import type { WeeklyLabelItem } from '../../api/weekly_results_service';

/** Figma "Cleared": green card with one white chip per food that looks fine. */
export function LooksFineCard({ items }: { items: WeeklyLabelItem[] }) {
  return (
    <View
      testID="looks-fine-card"
      className="w-full gap-3 rounded-[24px] border-[0.5px] border-remetra-fine-line bg-remetra-fine-bg p-4"
    >
      <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
        No pattern after plenty of clean, well-logged meals.
      </Text>
      <View className="flex-row flex-wrap gap-2">
        {items.map((item) => (
          <View key={item.id} testID={`looks-fine-${item.id}`} className="rounded-full bg-white px-4 py-2">
            <Text className="font-figtree text-[14px] leading-5 text-remetra-fine-text">{item.display_name}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}
