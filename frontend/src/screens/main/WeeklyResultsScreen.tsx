import { type ComponentRef, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { ChevronLeft } from 'lucide-react-native';
import { useFonts } from 'expo-font';
import { Prata_400Regular } from '@expo-google-fonts/prata';
import { Figtree_400Regular, Figtree_600SemiBold } from '@expo-google-fonts/figtree';
import { SkyBackground } from '../../components/weekly/SkyBackground';
import { InsightSection } from '../../components/weekly/InsightParts';
import { ProgressCard } from '../../components/weekly/ProgressCard';
import { AskEntryCard } from '../../components/weekly/AskEntryCard';
import { TriggerCard } from '../../components/weekly/TriggerCard';
import { LooksFineCard } from '../../components/weekly/LooksFineCard';
import { StillLearningCard } from '../../components/weekly/StillLearningCard';
import { useAppNavigation } from '../../navigation/hooks';
import { weeklyResultsService, WeeklyResultsResponse } from '../../api/weekly_results_service';
import { shortDate, weekdayDate, weeklyUpdateInfo } from '../../utils/weeklyUpdate';

/** Which message the screen leads with, if any. Decided from the labels only. */
export type WeeklyResultsState = 'empty' | 'no_clear_pattern' | 'results';

export function resultsState(results: WeeklyResultsResponse): WeeklyResultsState {
  const total = results.likely_trigger.length + results.still_learning.length + results.looks_fine.length;
  if (total === 0) return 'empty';
  if (results.no_clear_pattern) return 'no_clear_pattern';
  return 'results';
}

const STATE_MESSAGES: Record<Exclude<WeeklyResultsState, 'results'>, { title: string; body: string }> = {
  empty: {
    title: 'Your first results are on the way',
    body: 'Keep logging your meals and symptoms. Food groups show up here once you’ve eaten them a few times.',
  },
  no_clear_pattern: {
    title: 'No clear food pattern',
    body: 'Nothing you’ve eaten stands out as a trigger so far. Keep logging and we’ll let you know if that changes.',
  },
};

const TEXT_PRIMARY = '#3b2a24'; // remetra-text-primary

/** Figma "Insights" (Remetra Design, node 7192:356): the user's weekly food labels. */
export function WeeklyResultsScreen() {
  const navigation = useAppNavigation();
  const [fontsLoaded, fontError] = useFonts({ Prata_400Regular, Figtree_400Regular, Figtree_600SemiBold });
  const [results, setResults] = useState<WeeklyResultsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0); // bumped by "Try again" to refetch
  const scrollRef = useRef<ComponentRef<typeof ScrollView>>(null);

  useEffect(() => {
    weeklyResultsService
      .getWeekly()
      .then((data) => {
        setResults(data);
        setError(null);
      })
      .catch((err: any) => setError(err.message ?? 'Failed to fetch weekly results'))
      .finally(() => setIsLoading(false));
  }, [attempt]);

  const retry = () => {
    setIsLoading(true);
    setError(null);
    setAttempt((n) => n + 1);
  };

  // Text drawn before its font loads stays in the system font, so hold everything until the fonts are ready
  const fontsReady = fontsLoaded || Boolean(fontError);
  if (!fontsReady) {
    return (
      <View className="flex-1 bg-white">
        <ActivityIndicator testID="weekly-results-loading" color="#b2939b" style={{ marginTop: 120 }} />
      </View>
    );
  }

  const update = results?.first_meal_at ? weeklyUpdateInfo(new Date(results.first_meal_at)) : null;
  const eyebrow = update ? `Week ${update.week} update, ${shortDate(update.updateDate)}` : 'Weekly update';

  return (
    <View className="flex-1 bg-white">
      <SkyBackground />
      <ScrollView
        ref={scrollRef}
        contentContainerStyle={{ flexGrow: 1, paddingHorizontal: 16, paddingTop: 56, paddingBottom: 48 }}
      >
        {/* Figma "Top bar", with a back link because this screen is pushed from the Analysis tab */}
        <View className="w-full gap-[4px] px-[24px] py-[12px]">
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            accessibilityRole="button"
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            className="ml-[-6px] mb-[4px] flex-row items-center gap-[2px] self-start"
          >
            <ChevronLeft size={18} color={TEXT_PRIMARY} strokeWidth={2} />
            <Text className="font-figtree-semibold text-[14px] text-remetra-text-primary">Back</Text>
          </TouchableOpacity>
          {/* Figma "Titles": eyebrow and title, 2px apart */}
          <View className="gap-[2px]">
            <Text className="font-figtree-semibold text-[12px] uppercase leading-[16px] tracking-[0.96px] text-remetra-text-tertiary">
              {eyebrow}
            </Text>
            <Text className="font-prata text-[32px] leading-[40px] text-remetra-text-primary">Insights</Text>
          </View>
        </View>

        {isLoading ? (
          <ActivityIndicator testID="weekly-results-loading" color="#b2939b" style={{ marginTop: 48 }} />
        ) : error || !results ? (
          <View className="mt-[40px] items-center gap-[12px]">
            <Text className="text-center font-figtree text-[14px] text-remetra-rose">{error}</Text>
            <TouchableOpacity
              onPress={retry}
              accessibilityRole="button"
              className="rounded-full bg-remetra-primary px-[20px] py-[10px]"
            >
              <Text className="font-figtree-semibold text-[14px] text-white">Try again</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <WeeklyResultsBody
            results={results}
            nextUpdate={update ? weekdayDate(update.nextUpdateDate) : null}
            onSeeInsights={(y) => scrollRef.current?.scrollTo({ y, animated: true })}
          />
        )}
      </ScrollView>
    </View>
  );
}

function WeeklyResultsBody({
  results,
  nextUpdate,
  onSeeInsights,
}: {
  results: WeeklyResultsResponse;
  nextUpdate: string | null;
  onSeeInsights: (y: number) => void;
}) {
  const state = resultsState(results);
  const message = state === 'results' ? null : STATE_MESSAGES[state];
  // Where the results start inside the scroll view, so "See insights" can scroll to them
  const bodyY = useRef(0);
  const sectionsY = useRef(0);

  return (
    <View className="mt-[20px] gap-[20px]" onLayout={(e) => (bodyY.current = e.nativeEvent.layout.y)}>
      {state !== 'empty' && nextUpdate && (
        <ProgressCard
          checked={results.groups_checked}
          total={results.groups_total}
          nextUpdate={nextUpdate}
          onSeeInsights={() => onSeeInsights(bodyY.current + sectionsY.current - 16)}
        />
      )}
      <AskEntryCard />
      <View className="gap-[20px]" onLayout={(e) => (sectionsY.current = e.nativeEvent.layout.y)}>
        {message && (
          <View
            testID={`weekly-results-${state}`}
            className="w-full gap-[12px] rounded-[24px] border-[0.5px] border-remetra-line-subtle bg-white p-[20px]"
          >
            <Text className="font-prata text-[20px] leading-[28px] text-remetra-text-primary">{message.title}</Text>
            <Text className="font-figtree text-[14px] leading-[20px] text-remetra-text-secondary">{message.body}</Text>
          </View>
        )}
        {results.likely_trigger.length > 0 && (
          <InsightSection title="Likely trigger" testID="section-likely_trigger">
            {results.likely_trigger.map((item) => (
              <TriggerCard key={item.id} item={item} />
            ))}
          </InsightSection>
        )}
        {results.looks_fine.length > 0 && (
          <InsightSection title="Looks fine for you" testID="section-looks_fine">
            <LooksFineCard items={results.looks_fine} />
          </InsightSection>
        )}
        {results.still_learning.length > 0 && (
          <InsightSection title="Still learning" testID="section-still_learning">
            <StillLearningCard count={results.still_learning.length} />
          </InsightSection>
        )}
        {state !== 'empty' && (
          <Text className="text-center font-figtree text-[12px] leading-[16px] text-remetra-text-tertiary">
            These are patterns in your logs, not a diagnosis.
          </Text>
        )}
      </View>
    </View>
  );
}
