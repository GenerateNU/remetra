import type { FC, ReactNode } from 'react';
import { Text, View } from 'react-native';
import type { SvgProps } from 'react-native-svg';

// Pieces of the Figma "Insights" screen (Remetra Design, node 7192:356).

/** Figma "Overline": the small uppercase heading above each section. */
export function Overline({ children }: { children: string }) {
  return (
    <Text className="font-figtree-semibold text-[12px] uppercase leading-4 tracking-[0.96px] text-remetra-text-tertiary">
      {children}
    </Text>
  );
}

/** A section: overline heading, then its card. */
export function InsightSection({ title, children, testID }: { title: string; children: ReactNode; testID?: string }) {
  return (
    <View testID={testID} className="w-full gap-3">
      <Overline>{title}</Overline>
      {children}
    </View>
  );
}

/** Figma "Tag": white pill with a sparkle, at the top of an insight card. */
export function InsightTag({ label, color, Icon }: { label: string; color: string; Icon: FC<SvgProps> }) {
  return (
    <View className="flex-row items-center gap-2 self-start rounded-full bg-white px-3 py-1">
      <Icon width={14} height={14} />
      <Text style={{ color }} className="font-figtree-semibold text-[12px] leading-4 tracking-[0.12px]">
        {label}
      </Text>
    </View>
  );
}

/** Figma "Title/Small" and "Body/Regular" inside an insight card. */
export function InsightTitle({ children }: { children: string }) {
  return <Text className="font-prata text-[20px] leading-7 text-remetra-text-primary">{children}</Text>;
}

export function InsightBody({ children }: { children: string }) {
  return <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">{children}</Text>;
}
