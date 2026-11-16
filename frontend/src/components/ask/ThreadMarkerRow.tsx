import { Text, View } from 'react-native';
import { SparkleChipIcon } from './icons';
import type { ThreadMarker } from '../../types/chat';

/** Figma "Ask / Context chip" (entry point) and "Ask / Day label" (timestamp or conversation marker). */
export function ThreadMarkerRow({ marker }: { marker: ThreadMarker }) {
  return (
    <View className="w-full flex-row justify-center">
      {marker.kind === 'context' ? (
        <View className="flex-row items-center gap-1.5 rounded-full border border-remetra-dawn bg-white px-3 py-1.5">
          <SparkleChipIcon width={13} height={13} />
          <Text className="font-figtree-semibold text-[12px] text-remetra-chip-strong">{marker.label}</Text>
        </View>
      ) : (
        <Text className="font-figtree-semibold text-[12px] uppercase tracking-[0.72px] text-remetra-text-tertiary">
          {marker.label}
        </Text>
      )}
    </View>
  );
}
