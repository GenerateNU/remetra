import { Pressable, Text } from 'react-native';

const PRIMARY_SHADOW = {
  shadowColor: '#63311F',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.06,
  shadowRadius: 4,
  elevation: 2,
};

/**
 * Figma "Button". Primary is one per screen; ghost is the alternative.
 * `fill` is for side-by-side buttons inside cards, where the design's labels
 * run past the 24px padding.
 */
export function PillButton({
  label,
  onPress,
  variant = 'primary',
  fill = false,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'ghost';
  fill?: boolean;
  disabled?: boolean;
}) {
  const primary = variant === 'primary';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      className={`items-center justify-center rounded-full py-4 ${fill ? 'flex-1 px-2' : 'px-6'} ${
        primary ? 'border border-remetra-ember bg-remetra-primary' : 'border-2 border-remetra-dawn bg-remetra-canvas'
      }`}
      style={({ pressed }) => ({
        ...(primary ? PRIMARY_SHADOW : null),
        opacity: disabled ? 0.6 : pressed ? 0.88 : 1,
      })}
    >
      <Text
        numberOfLines={1}
        className={`font-figtree-semibold text-[16px] leading-5 tracking-[0.16px] ${
          primary ? 'text-white' : 'text-remetra-primary'
        }`}
      >
        {label}
      </Text>
    </Pressable>
  );
}
