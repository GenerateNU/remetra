import { ScrollView, View } from 'react-native';
import { ChoiceChip, OnboardingChrome } from './OnboardingChrome';
import { SUSPICION_OPTIONS, useOnboardingStore } from '../../store/onboardingStore';
import { useAppNavigation } from '../../navigation/hooks';

export function SuspicionsScreen() {
  const navigation = useAppNavigation();
  const suspicions = useOnboardingStore((state) => state.suspicions);
  const toggleSuspicion = useOnboardingStore((state) => state.toggleSuspicion);
  const goNext = () => navigation.navigate('Regulars');

  return (
    <OnboardingChrome
      step={3}
      title="Foods you suspect bother you"
      subtitle="Optional. These give us a starting nudge, not a verdict. Suspicions are often wrong, and that’s okay."
      primaryLabel="Continue"
      onBack={() => navigation.goBack()}
      onPrimary={goNext}
      onSkip={goNext}
    >
      <ScrollView showsVerticalScrollIndicator={false} contentContainerClassName="pb-6">
        <View className="flex-row flex-wrap gap-3">
          {SUSPICION_OPTIONS.map((option) => (
            <ChoiceChip
              key={option}
              label={option}
              removable
              selected={suspicions.includes(option)}
              onPress={() => toggleSuspicion(option)}
            />
          ))}
        </View>
      </ScrollView>
    </OnboardingChrome>
  );
}
