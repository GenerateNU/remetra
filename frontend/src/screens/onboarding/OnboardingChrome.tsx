import { ReactNode } from 'react';
import { Pressable, Text, View } from 'react-native';
import { useFonts } from 'expo-font';
import { StatusBar } from 'expo-status-bar';
import { Prata_400Regular } from '@expo-google-fonts/prata';
import { Figtree_400Regular, Figtree_600SemiBold } from '@expo-google-fonts/figtree';
import { LinearGradient } from 'expo-linear-gradient';
import { Check, ChevronLeft, X } from 'lucide-react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const BUTTON_SHADOW = {
  shadowColor: '#63311F',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.06,
  shadowRadius: 8,
  elevation: 2,
};

const PROGRESS_COLORS = ['#c42f55', '#f2875a', '#ffe09e'] as const;

export function OnboardingChrome({
  step,
  title,
  subtitle,
  children,
  primaryLabel,
  onBack,
  onPrimary,
  onSkip,
  primaryDisabled = false,
}: {
  step: 1 | 2 | 3 | 4;
  title: string;
  subtitle: string;
  children: ReactNode;
  primaryLabel: string;
  onBack: () => void;
  onPrimary: () => void;
  onSkip: () => void;
  primaryDisabled?: boolean;
}) {
  const insets = useSafeAreaInsets();
  const [fontsLoaded, fontError] = useFonts({
    Prata_400Regular,
    Figtree_400Regular,
    Figtree_600SemiBold,
  });

  if (!fontsLoaded && !fontError) {
    return null;
  }

  return (
    <View className="flex-1 bg-remetra-sheet">
      <StatusBar style="dark" />
      <LinearGradient
        colors={['#fdddcc', '#fef0e7', '#faf8f6']}
        locations={[0, 0.5, 1]}
        style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 340 }}
      />

      <View
        className="flex-1 px-6"
        style={{ paddingTop: insets.top + 12, paddingBottom: Math.max(insets.bottom, 12) }}
      >
        <View className="flex-row items-center gap-3">
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Back"
            onPress={onBack}
            className="h-[38px] w-[38px] items-center justify-center rounded-full border border-remetra-line-subtle bg-white"
          >
            <ChevronLeft size={20} color="#3b2a24" strokeWidth={1.75} />
          </Pressable>
          <View className="flex-1 flex-row gap-2">
            {[0, 1, 2, 3].map((index) =>
              index < step ? (
                <LinearGradient
                  key={index}
                  colors={PROGRESS_COLORS}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={{ flex: 1, height: 4, borderRadius: 999 }}
                />
              ) : (
                <View key={index} className="h-1 flex-1 rounded-full bg-remetra-sheet" />
              )
            )}
          </View>
          <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
            {step} of 4
          </Text>
        </View>

        <View className="mt-6 gap-3 py-2">
          <Text className="font-prata text-[32px] leading-[40px] text-remetra-text-primary">
            {title}
          </Text>
          <Text className="font-figtree text-[14px] leading-5 text-remetra-text-secondary">
            {subtitle}
          </Text>
        </View>

        <View className="mt-4 flex-1">{children}</View>

        <View className="gap-1 pt-4">
          <Text className="text-center font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
            This helps us start in the right place. You can change it anytime.
          </Text>
          <Pressable
            accessibilityRole="button"
            disabled={primaryDisabled}
            onPress={onPrimary}
            className="w-full items-center justify-center rounded-full border border-remetra-ember bg-remetra-primary px-6 py-4"
            style={({ pressed }) => ({
              ...BUTTON_SHADOW,
              opacity: primaryDisabled ? 0.6 : pressed ? 0.88 : 1,
            })}
          >
            <Text className="font-figtree-semibold text-[16px] leading-5 tracking-[0.16px] text-white">
              {primaryLabel}
            </Text>
          </Pressable>
          <Pressable
            accessibilityRole="button"
            onPress={onSkip}
            className="w-full items-center justify-center rounded-full px-2 py-4"
            style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}
          >
            <Text className="font-figtree-semibold text-[16px] leading-5 tracking-[0.16px] text-remetra-primary">
              Skip for now
            </Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

export function ChoiceChip({
  label,
  selected,
  removable = false,
  onPress,
}: {
  label: string;
  selected: boolean;
  removable?: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected }}
      onPress={onPress}
      className={`flex-row items-center gap-2 rounded-full px-4 py-2 ${
        selected
          ? 'border-2 border-remetra-peach-line bg-remetra-canvas'
          : 'border border-remetra-chip-line bg-white'
      }`}
    >
      {selected ? <Check size={16} color="#92472a" strokeWidth={2.25} /> : null}
      <Text
        className={`text-[14px] leading-5 ${
          selected
            ? 'font-figtree-semibold tracking-[0.14px] text-remetra-chip-strong'
            : 'font-figtree text-remetra-text-primary'
        }`}
      >
        {label}
      </Text>
      {selected && removable ? <X size={14} color="#92472a" strokeWidth={2.25} /> : null}
    </Pressable>
  );
}
