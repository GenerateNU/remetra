import { ScrollView, View } from 'react-native';
import { ChoiceChip, OnboardingChrome } from './OnboardingChrome';
import { CONDITION_OPTIONS, useOnboardingStore } from '../../store/onboardingStore';
import { useAppNavigation } from '../../navigation/hooks';

export function ConditionsScreen() {
  const navigation = useAppNavigation();
  const conditions = useOnboardingStore((state) => state.conditions);
  const toggleCondition = useOnboardingStore((state) => state.toggleCondition);

  const goNext = () => navigation.navigate('Exclusions');

  return (
    <OnboardingChrome
      step={1}
      title="Anything you’ve been diagnosed with?"
      subtitle="Select all that apply."
      primaryLabel="Continue"
      onBack={() => navigation.goBack()}
      onPrimary={goNext}
      onSkip={goNext}
    >
      <ScrollView showsVerticalScrollIndicator={false} contentContainerClassName="pb-6">
        <View className="flex-row flex-wrap gap-3">
          {CONDITION_OPTIONS.map((option) => (
            <ChoiceChip
              key={option}
              label={option}
              selected={conditions.includes(option)}
              onPress={() => toggleCondition(option)}
            />
          ))}
        </View>
      </ScrollView>
    </OnboardingChrome>
  );
}
