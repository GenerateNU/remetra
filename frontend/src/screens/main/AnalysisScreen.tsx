import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { SymptomsOverTimeChart } from '../../components/SymptomsOverTimeChart';
import { symptomLogService, SymptomLogResponse } from '../../api/symptom_log_service';
import { foodLogService } from '../../api/food_log_service';
import { useBankStore } from '../../store/bankStore';
import { useAuthStore } from '../../store/useAuthStore';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';
import { useAppNavigation } from '../../navigation/hooks';
import { ChevronRight } from 'lucide-react-native';

const MIN_LOGS_FOR_ANALYSIS = 30;

interface SymptomCount {
  symptomId: string;
  name: string;
  location: string;
  sensation: string;
  count: number;
  avgIntensity: number;
}

export function AnalysisScreen() {
  const { symptoms, fetchSymptoms } = useBankStore();
  const username = useAuthStore((s) => s.user.name);
  const { runAlgorithm } = useAlgorithmStore();
  const [symptomCounts, setSymptomCounts] = useState<SymptomCount[]>([]);
  const [symptomLogs, setSymptomLogs] = useState<SymptomLogResponse[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        await fetchSymptoms();
        const [logs, foodLogs] = await Promise.all([
          symptomLogService.getMySymptomLogs(),
          foodLogService.getMyFoodLogs(),
        ]);

        const total = logs.length + foodLogs.length;
        setTotalLogs(total);

        if (total < MIN_LOGS_FOR_ANALYSIS) {
          setSymptomLogs(logs);
          return;
        }

        const countMap: Record<string, number> = {};
        const intensityMap: Record<string, number[]> = {};
        for (const log of logs) {
          countMap[log.symptom_id] = (countMap[log.symptom_id] ?? 0) + 1;
          if (!intensityMap[log.symptom_id]) intensityMap[log.symptom_id] = [];
          intensityMap[log.symptom_id].push(log.intensity);
        }

        const counts: SymptomCount[] = useBankStore
          .getState()
          .symptoms.map((s) => {
            const intensities = intensityMap[s.id] ?? [];
            const avg = intensities.length > 0
              ? intensities.reduce((a, b) => a + b, 0) / intensities.length
              : 0;
            return {
              symptomId: s.id,
              name: s.name,
              location: s.location,
              sensation: s.sensation,
              count: countMap[s.id] ?? 0,
              avgIntensity: Math.round(avg * 10) / 10,
            };
          })
          .filter((s) => s.count > 0)
          .sort((a, b) => b.count - a.count);

        setSymptomCounts(counts);
        setSymptomLogs(logs);

        if (username) {
          runAlgorithm(username).catch(() => {});
        }
      } catch (err: any) {
        setError(err.message ?? 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const belowThreshold = totalLogs < MIN_LOGS_FOR_ANALYSIS;

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>
        <Text className="text-2xl font-semibold text-remetra-mauve italic tracking-[1px] text-center mb-8">
          YOUR ANALYSIS
        </Text>

        <SectionDivider label="Symptoms by Occurrences"/>

        {loading ? (
          <ActivityIndicator color="#b2939b" style={{ marginTop: 24 }} />
        ) : error ? (
          <Text className="text-remetra-burgundy text-center mt-6">{error}</Text>
        ) : belowThreshold ? (
          <View className="bg-white/35 rounded-xl p-5 mt-4">
            <Text className="text-remetra-mauve text-center text-base font-semibold mb-2">
              Keep logging to unlock your analysis
            </Text>
            <Text className="text-remetra-muted text-center text-sm">
              You need at least {MIN_LOGS_FOR_ANALYSIS} total logs (food + symptoms) before we can run your analysis.
              {'\n\n'}
              You currently have {totalLogs} — {MIN_LOGS_FOR_ANALYSIS - totalLogs} more to go.
            </Text>
          </View>
        ) : symptomCounts.length === 0 ? (
          <Text className="text-remetra-muted text-center mt-6 text-sm">
            No symptoms logged yet.
          </Text>
        ) : (
          <>
            <SymptomsOverTimeChart
              logs={symptomLogs}
              symptomNames={Object.fromEntries(symptomCounts.map(s => [s.symptomId, s.name]))}
            />

            <SectionDivider label="Details" />
            <View className="gap-2.5">
              {symptomCounts.map((item, index) => (
                <SymptomRow key={item.symptomId} rank={index + 1} item={item} />
              ))}
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View className="flex-row items-center mb-3">
      <Text className="text-xs text-remetra-espresso mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-white" />
    </View>
  );
}

function SymptomRow({ rank, item }: { rank: number; item: SymptomCount }) {
  const navigation = useAppNavigation();
  const subtitle = item.avgIntensity > 0
    ? `Avg severity: ${item.avgIntensity.toFixed(1)} / 10`
    : null;

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('Correlations', { initialSymptomId: item.symptomId })}
      className="bg-white/35 rounded-xl p-4 flex-row items-center gap-3"
    >
      <Text className="text-sm font-bold text-remetra-mauve w-6 text-center">{rank}</Text>
      <View className="flex-1">
        <Text className="text-[15px] text-remetra-espresso font-semibold">{item.name}</Text>
        {subtitle ? (
          <Text className="text-xs text-remetra-warm-brown mt-0.5">{subtitle}</Text>
        ) : null}
      </View>
      <View className="bg-remetra-peach rounded-full px-2.5 py-1 min-w-9 items-center">
        <Text className="text-sm font-bold text-remetra-rose">{item.count}</Text>
      </View>
      <ChevronRight size={16} color="#5C2E14" strokeWidth={2} />
    </TouchableOpacity>
  );
}
