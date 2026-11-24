import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { ArrowLeft } from 'lucide-react-native';
import { useFonts } from 'expo-font';
import { Prata_400Regular } from '@expo-google-fonts/prata';
import { Figtree_400Regular, Figtree_600SemiBold } from '@expo-google-fonts/figtree';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import {
  LabelListCard,
  LikelyTriggerCard,
  NoClearPatternCard,
  StillLearningEmptyCard,
} from '../../components/results/WeeklyResultsCards';
import { resultsService } from '../../api/results_service';
import type { WeeklyResultsResponse } from '../../types/weeklyResults';

/** Loads GET /results/weekly and shows it. */
export function WeeklyResultsScreen({ onBack }: { onBack?: () => void }) {
  const [results, setResults] = useState<WeeklyResultsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State only changes once the request settles, so the effect never sets state synchronously.
  const fetchResults = useCallback(
    () =>
      resultsService
        .getWeeklyResults()
        .then((data) => {
          setResults(data);
          setError(null);
        })
        .catch((err: any) => setError(err.message ?? 'Failed to load your weekly results'))
        .finally(() => setIsLoading(false)),
    [],
  );

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  const retry = useCallback(() => {
    setIsLoading(true);
    setError(null);
    fetchResults();
  }, [fetchResults]);

  return <WeeklyResultsView results={results} isLoading={isLoading} error={error} onBack={onBack} onRetry={retry} />;
}

interface ViewProps {
  /** Missing results show the still learning empty state. */
  results?: WeeklyResultsResponse | null;
  isLoading?: boolean;
  error?: string | null;
  onBack?: () => void;
  onRetry?: () => void;
}

/** Weekly results: each food the user has eaten, by label. Labels only, never confidence numbers. */
export function WeeklyResultsView({ results = null, isLoading = false, error = null, onBack, onRetry }: ViewProps) {
  const insets = useSafeAreaInsets();
  const [fontsLoaded, fontError] = useFonts({ Prata_400Regular, Figtree_400Regular, Figtree_600SemiBold });
  if (!fontsLoaded && !fontError) return null;

  return (
    <View className="flex-1 bg-remetra-canvas">
      <ScrollView contentContainerStyle={{ paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 }}>
        <View className="gap-1 px-6 pb-5">
          {onBack ? (
            <TouchableOpacity
              onPress={onBack}
              accessibilityRole="button"
              accessibilityLabel="Back"
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              className="mb-2 flex-row items-center gap-1.5 self-start"
            >
              <ArrowLeft size={16} color="#b5582f" strokeWidth={2} />
              <Text className="font-figtree text-[14px] text-remetra-primary">Back</Text>
            </TouchableOpacity>
          ) : null}
          <Text className="font-figtree-semibold text-[11px] uppercase tracking-[0.88px] text-remetra-text-tertiary">
            This week
          </Text>
          <Text className="font-prata text-[28px] leading-9 text-remetra-text-primary">Your food results</Text>
        </View>

        <View className="gap-4 px-4">
          {isLoading ? (
            <ActivityIndicator testID="weekly-results-loading" color="#b2939b" style={{ marginTop: 48 }} />
          ) : error ? (
            <View className="mt-10 items-center gap-3">
              <Text className="text-center font-figtree text-[14px] text-remetra-rose">{error}</Text>
              {onRetry ? (
                <TouchableOpacity
                  onPress={onRetry}
                  accessibilityRole="button"
                  className="rounded-full border border-remetra-chip-line bg-white px-4 py-2"
                >
                  <Text className="font-figtree-semibold text-[13px] text-remetra-primary">Try again</Text>
                </TouchableOpacity>
              ) : null}
            </View>
          ) : (
            <ResultsBody results={results} />
          )}
        </View>
      </ScrollView>
    </View>
  );
}

function ResultsBody({ results }: { results: WeeklyResultsResponse | null }) {
  if (!results) return <StillLearningEmptyCard />;
  const { likely_trigger, still_learning, looks_fine, no_clear_pattern } = results;
  if (likely_trigger.length + still_learning.length + looks_fine.length === 0) {
    return <StillLearningEmptyCard />;
  }
  return (
    <>
      {no_clear_pattern ? <NoClearPatternCard /> : null}
      {likely_trigger.map((item) => (
        <LikelyTriggerCard key={item.id} item={item} />
      ))}
      <LabelListCard label="still_learning" items={still_learning} />
      <LabelListCard label="looks_fine" items={looks_fine} />
    </>
  );
}
