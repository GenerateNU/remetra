import { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { ChoiceChip, OnboardingChrome } from './OnboardingChrome';
import { NONE_CONDITION, REGULAR_OPTIONS, useOnboardingStore } from '../../store/onboardingStore';
import { useAuthStore } from '../../store/useAuthStore';
import { authService } from '../../api/auth_service';
import { useAppNavigation } from '../../navigation/hooks';

export function RegularsScreen() {
  const navigation = useAppNavigation();
  const [saving, setSaving] = useState(false);
  const regulars = useOnboardingStore((state) => state.regulars);
  const toggleRegular = useOnboardingStore((state) => state.toggleRegular);
  const completeOnboarding = useAuthStore((state) => state.completeOnboarding);
  const updateUserProfile = useAuthStore((state) => state.updateUserProfile);

  const finish = async () => {
    if (saving) return;
    setSaving(true);
    const conditions = useOnboardingStore
      .getState()
      .conditions.filter((condition) => condition !== NONE_CONDITION);
    try {
      if (conditions.length > 0) {
        const me = await authService.updateProfile({ disease: conditions });
        updateUserProfile({ disease: me.disease ?? conditions });
      }
    } catch {
      // The local flag still lets them into the app if the profile save fails.
    }
    completeOnboarding();
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
