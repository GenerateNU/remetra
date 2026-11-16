import { useRef, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { ChoiceChip, OnboardingChrome } from './OnboardingChrome';
import { onboardingAnswers } from './onboardingAnswers';
import { REGULAR_OPTIONS, useOnboardingStore } from '../../store/onboardingStore';
import { useAuthStore } from '../../store/useAuthStore';
import { ApiError } from '../../api/client';
import { authService } from '../../api/auth_service';
import { ingredientService } from '../../api/ingredient_service';
import { useAppNavigation } from '../../navigation/hooks';

export function RegularsScreen() {
  const navigation = useAppNavigation();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const savingRef = useRef(false);
  const regulars = useOnboardingStore((state) => state.regulars);
  const toggleRegular = useOnboardingStore((state) => state.toggleRegular);
  const completeOnboarding = useAuthStore((state) => state.completeOnboarding);
  const updateUserProfile = useAuthStore((state) => state.updateUserProfile);

  const finish = async () => {
    if (savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setError(null);
    const answers = onboardingAnswers(useOnboardingStore.getState());
    try {
      await ingredientService.replaceLabels({
        avoid: answers.avoid,
        suspect: answers.suspect,
        safe: answers.safe,
      });
      const me = await authService.updateProfile({ disease: answers.disease });
      if (me.disease == null) {
        throw new ApiError('Could not save your answers. Please try again.');
      }
      updateUserProfile({ disease: me.disease });
      completeOnboarding();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save your answers. Please try again.');
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  };

  return (
    <OnboardingChrome
      step={4}
      title="Foods you eat regularly"
      subtitle="Tap the groups you already eat. Only these can show up in your dinners."
      primaryLabel="See tonight’s dinner"
      primaryDisabled={saving}
      onBack={() => navigation.goBack()}
      onPrimary={finish}
      onSkip={finish}
    >
      <ScrollView showsVerticalScrollIndicator={false} contentContainerClassName="pb-6">
        {error ? (
          <Text className="mb-4 font-figtree text-[14px] leading-5 text-red-400">{error}</Text>
        ) : null}
        <View className="flex-row flex-wrap gap-3">
          {REGULAR_OPTIONS.map((option) => (
            <ChoiceChip
              key={option}
              label={option}
              selected={regulars.includes(option)}
              onPress={() => toggleRegular(option)}
            />
          ))}
        </View>
      </ScrollView>
    </OnboardingChrome>
  );
}
