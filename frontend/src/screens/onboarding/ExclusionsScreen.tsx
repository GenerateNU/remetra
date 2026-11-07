import { useState } from 'react';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { Lock, Search } from 'lucide-react-native';
import { OnboardingChrome } from './OnboardingChrome';
import {
  CELIAC,
  EXCLUSION_CATALOG,
  LOCKED_GLUTEN,
  useOnboardingStore,
} from '../../store/onboardingStore';
import { useAppNavigation } from '../../navigation/hooks';

export function ExclusionsScreen() {
  const navigation = useAppNavigation();
  const [query, setQuery] = useState('');
  const conditions = useOnboardingStore((state) => state.conditions);
  const exclusions = useOnboardingStore((state) => state.exclusions);
  const addExclusion = useOnboardingStore((state) => state.addExclusion);
  const setExclusionAllergic = useOnboardingStore((state) => state.setExclusionAllergic);
  const hasCeliac = conditions.includes(CELIAC);
  const trimmed = query.trim();
  const matches = trimmed
    ? EXCLUSION_CATALOG.filter((name) => {
        if (hasCeliac && name === LOCKED_GLUTEN) return false;
        if (exclusions.some((item) => item.name === name)) return false;
        return name.toLowerCase().includes(trimmed.toLowerCase());
      })
    : [];

  const goNext = () => navigation.navigate('Suspicions');

  return (
    <OnboardingChrome
      step={2}
      title="Foods you can’t or won’t eat"
      subtitle="We’ll never put these in a dinner."
      primaryLabel="Continue"
      onBack={() => navigation.goBack()}
      onPrimary={goNext}
      onSkip={goNext}
    >
      <ScrollView showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled" contentContainerClassName="gap-4 pb-6">
        <View className="h-[58px] flex-row items-center gap-3 rounded-full border border-remetra-chip-line bg-white px-4">
          <Search size={20} color="#7a7068" strokeWidth={1.75} />
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search ingredients or food groups"
            placeholderTextColor="#7a7068"
            className="flex-1 font-figtree text-[16px] text-remetra-text-primary"
            autoCorrect={false}
            returnKeyType="search"
          />
        </View>

        {matches.length > 0 ? (
          <View className="overflow-hidden rounded-2xl border border-remetra-chip-line bg-white">
            {matches.map((name, index) => (
              <Pressable
                key={name}
                accessibilityRole="button"
                onPress={() => {
                  addExclusion(name);
                  setQuery('');
                }}
                className={`px-4 py-3 ${index < matches.length - 1 ? 'border-b border-remetra-line-subtle' : ''}`}
              >
                <Text className="font-figtree text-[16px] leading-5 text-remetra-text-primary">{name}</Text>
              </Pressable>
            ))}
          </View>
        ) : null}

        {hasCeliac ? (
          <View className="flex-row items-start gap-3 rounded-2xl bg-remetra-canvas px-4 py-3">
            <Lock size={18} color="#7a7068" strokeWidth={1.75} style={{ marginTop: 1 }} />
            <Text className="flex-1 font-figtree text-[14px] leading-5 text-remetra-text-secondary">
              Gluten stays off your plan because you have celiac disease.
            </Text>
          </View>
        ) : null}

        {exclusions.length > 0 ? (
          <View className="overflow-hidden rounded-[20px] border border-remetra-chip-line bg-white">
            {exclusions.map((item, index) => (
              <View
                key={item.name}
                className={`flex-row items-center justify-between px-4 py-3 ${
                  index < exclusions.length - 1 ? 'border-b border-remetra-line-subtle' : ''
                }`}
              >
                <View className="mr-3 flex-1">
                  <Text className="font-figtree-semibold text-[16px] leading-5 text-remetra-text-primary">
                    {item.name}
                  </Text>
                  <Text className="font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
                    {item.allergic ? 'Allergic: never introduced' : 'Won’t eat'}
                  </Text>
                </View>
                <View className="flex-row items-center gap-2">
                  <Text className="font-figtree text-[12px] leading-4 text-remetra-text-secondary">
                    I’m allergic
                  </Text>
                  <Pressable
                    accessibilityRole="switch"
                    accessibilityState={{ checked: item.allergic }}
                    accessibilityLabel={`I’m allergic to ${item.name}`}
                    onPress={() => setExclusionAllergic(item.name, !item.allergic)}
                    className={`h-[26px] w-11 justify-center rounded-full px-1 ${
                      item.allergic ? 'bg-remetra-peach-line' : 'bg-remetra-chip-line'
                    }`}
                  >
                    <View
                      className="h-5 w-5 rounded-full bg-white"
                      style={{ transform: [{ translateX: item.allergic ? 18 : 0 }] }}
                    />
                  </Pressable>
                </View>
              </View>
            ))}
          </View>
        ) : null}
      </ScrollView>
    </OnboardingChrome>
  );
}
