import { ReactNode } from 'react';
import { Text, View } from 'react-native';
import { CheckSuccessIcon } from '../icons';

/** White card used by the calendar, recipe, ideas, draft, symptom and summary attachments. */
export function CardShell({ children, strongBorder = false }: { children: ReactNode; strongBorder?: boolean }) {
  return (
    <View
      className={`w-full gap-2.5 rounded-[20px] border bg-white px-4 py-3.5 ${
        strongBorder ? 'border-remetra-chip-line' : 'border-remetra-line-subtle'
      }`}
    >
      {children}
    </View>
  );
}

export function Eyebrow({ children }: { children: string }) {
  return (
    <Text className="font-figtree-semibold text-[11px] uppercase tracking-[0.88px] text-remetra-text-tertiary">
      {children}
    </Text>
  );
}

export function CardTitle({ children }: { children: string }) {
  return <Text className="font-prata text-[18px] leading-6 text-remetra-text-primary">{children}</Text>;
}

/** Rows inside a card list: every row after the first gets a hairline above it. */
export function ListRow({ first, children, className = '' }: { first: boolean; children: ReactNode; className?: string }) {
  return (
    <View className={`flex-row ${first ? '' : 'border-t border-remetra-line-subtle pt-[7px]'} ${className}`}>
      {children}
    </View>
  );
}

export function FieldRow({ first, label, children }: { first: boolean; label: string; children: ReactNode }) {
  return (
    <ListRow first={first} className="items-center justify-between">
      <Text className="font-figtree text-[13px] text-remetra-text-tertiary">{label}</Text>
      {children}
    </ListRow>
  );
}

export function FieldValue({ children }: { children: string }) {
  return (
    <Text className="flex-1 pl-3 text-right font-figtree-semibold text-[13px] text-remetra-text-primary">{children}</Text>
  );
}

export function ButtonRow({ children }: { children: ReactNode }) {
  return <View className="w-full flex-row gap-2">{children}</View>;
}

/** Figma "Ask / Saved state". */
export function SavedBanner({ text }: { text: string }) {
  return (
    <View className="w-full flex-row items-center gap-2 rounded-[14px] bg-remetra-fine-bg px-3 py-2.5">
      <CheckSuccessIcon width={16} height={16} />
      <Text className="flex-1 font-figtree-semibold text-[13px] text-remetra-fine-text">{text}</Text>
    </View>
  );
}

export function ErrorNote({ children }: { children: string }) {
  return <Text className="font-figtree text-[12px] leading-4 text-remetra-rose">{children}</Text>;
}
