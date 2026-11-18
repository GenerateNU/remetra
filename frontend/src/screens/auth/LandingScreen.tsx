import { View, Text, Pressable } from 'react-native';
import { useFonts } from 'expo-font';
import { StatusBar } from 'expo-status-bar';
import { Prata_400Regular } from '@expo-google-fonts/prata';
import { Figtree_400Regular, Figtree_600SemiBold } from '@expo-google-fonts/figtree';
import Svg, { Circle, Defs, RadialGradient, Stop } from 'react-native-svg';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAppNavigation } from '../../navigation/hooks';

const SUN_SIZE = 276;
const HALO_SIZE = 530;
const HALO_INSET = (HALO_SIZE - SUN_SIZE) / 2;

const BUTTON_SHADOW = {
  shadowColor: '#63311F',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.06,
  shadowRadius: 8,
  elevation: 2,
};

function Halo() {
  return (
    <Svg width={HALO_SIZE} height={HALO_SIZE} viewBox="0 0 460 460">
      <Defs>
        <RadialGradient id="welcomeHalo" cx="50%" cy="50%" r="50%">
          <Stop offset="0" stopColor="#F7A35C" stopOpacity={0.55} />
          <Stop offset="0.55" stopColor="#FFE3A6" stopOpacity={0.3} />
          <Stop offset="1" stopColor="#FFE3A6" stopOpacity={0} />
        </RadialGradient>
      </Defs>
      <Circle cx={230} cy={230} r={230} fill="url(#welcomeHalo)" />
    </Svg>
  );
}

function Sun() {
  return (
    <Svg width={SUN_SIZE} height={SUN_SIZE} viewBox="0 0 240 240">
      <Defs>
        <RadialGradient id="welcomeSun" cx="50%" cy="50%" r="50%">
          <Stop offset="0" stopColor="#F26A5B" />
          <Stop offset="0.35" stopColor="#F7A35C" />
          <Stop offset="0.68" stopColor="#FFE3A6" stopOpacity={0.85} />
          <Stop offset="1" stopColor="#FFE3A6" stopOpacity={0} />
        </RadialGradient>
      </Defs>
      <Circle cx={120} cy={120} r={120} fill="url(#welcomeSun)" />
    </Svg>
  );
}

export function LandingScreen() {
  const navigation = useAppNavigation();
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
    <View className="flex-1 bg-remetra-canvas">
      <StatusBar style="dark" />

      <View className="flex-1 items-center justify-center" pointerEvents="none">
        <View style={{ width: SUN_SIZE, height: SUN_SIZE }}>
          <View style={{ position: 'absolute', top: -HALO_INSET, left: -HALO_INSET }}>
            <Halo />
          </View>
          <Sun />
        </View>
      </View>

      <View
        className="items-center px-8"
        style={{ paddingBottom: Math.max(insets.bottom + 16, 52) }}
      >
        <View className="w-full max-w-[329px]">
          <View className="items-center gap-5">
            <Text
              className="font-prata text-[24px] uppercase leading-[32px] tracking-[9.6px] text-remetra-primary"
              style={{ marginRight: -9.6 }}
            >
              Remetra
            </Text>
            <Text className="text-center font-prata text-[40px] leading-[48px] text-remetra-text-primary">
              Peace of mind begins here.
            </Text>
            <Text className="text-center font-figtree text-[16px] leading-[24px] text-remetra-text-secondary">
              Find the foods that work for your body, one gentle evening at a time.
            </Text>
          </View>

          <View className="mt-4 gap-2">
            <Pressable
              accessibilityRole="button"
              onPress={() => navigation.navigate('Signup')}
              className="w-full items-center justify-center rounded-full border border-remetra-ember bg-remetra-primary px-6 py-4"
              style={({ pressed }) => ({
                ...BUTTON_SHADOW,
                opacity: pressed ? 0.88 : 1,
              })}
            >
              <Text className="font-figtree-semibold text-[16px] leading-[20px] tracking-[0.16px] text-white">
                Get started
              </Text>
            </Pressable>

            <Pressable
              accessibilityRole="button"
              onPress={() => navigation.navigate('Login')}
              className="w-full items-center justify-center rounded-full px-2 py-4"
              style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}
            >
              <Text className="font-figtree-semibold text-[16px] leading-[20px] tracking-[0.16px] text-remetra-primary">
                I already have an account
              </Text>
            </Pressable>
          </View>
        </View>
      </View>
    </View>
  );
}
