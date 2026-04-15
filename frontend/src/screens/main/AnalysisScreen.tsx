import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { FrequencyIntensityChart } from '../../components/FrequencyIntensityChart';
import { useBankStore } from '../../store/bankStore';
import { symptomLogService } from '../../api/symptom_log_service';
import { useAuthStore } from '../../store/useAuthStore';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';
import { useAppNavigation } from '../../navigation/hooks';

interface SymptomCount {
  symptomId: string;
  name: string;
  location: string;
  sensation: string;
  count: number;
}

export function AnalysisScreen() {
  const { symptoms, fetchSymptoms } = useBankStore();
  const username = useAuthStore((s) => s.user.name);
  const { associationsBySymptom, runAlgorithm } = useAlgorithmStore();
  const [symptomCounts, setSymptomCounts] = useState<SymptomCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        await fetchSymptoms();
        const logs = await symptomLogService.getMySymptomLogs();

        const countMap: Record<string, number> = {};
        for (const log of logs) {
          countMap[log.symptom_id] = (countMap[log.symptom_id] ?? 0) + 1;
        }

        const counts: SymptomCount[] = useBankStore
          .getState()
          .symptoms.map((s) => ({
            symptomId: s.id,
            name: s.name,
            location: s.location,
            sensation: s.sensation,
            count: countMap[s.id] ?? 0,
          }))
          .filter((s) => s.count > 0)
          .sort((a, b) => b.count - a.count);

        setSymptomCounts(counts);

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
        ) : symptomCounts.length === 0 ? (
          <Text className="text-remetra-muted text-center mt-6 text-sm">
            No symptoms logged yet.
          </Text>
        ) : (
          <>
            {/* Symptom overview: instances vs avg intensity */}
            {(() => {
              const scatterData = symptomCounts
                .map(s => {
                  const assocs = associationsBySymptom[s.symptomId] ?? [];
                  if (assocs.length === 0) return null;
                  const avgIntensity = assocs.reduce((sum, a) => sum + a.average_intensity, 0) / assocs.length;
                  return { ingredient_name: s.name, exposures: s.count, average_intensity: avgIntensity };
                })
                .filter((d): d is NonNullable<typeof d> => d !== null);

              return scatterData.length >= 2 ? (
                <FrequencyIntensityChart data={scatterData} />
              ) : null;
            })()}

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
      <Text className="text-xs font-bold text-remetra-muted mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-neutral-200" />
    </View>
  );
}

function SymptomRow({ rank, item }: { rank: number; item: SymptomCount }) {
  const navigation = useAppNavigation();
  // Add backend route to return avg intensity for symptoms
  const subtitle = "Average Intensity: "

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('Correlations', { initialSymptomId: item.symptomId })}
      className="bg-white/35 rounded-xl p-4 flex-row items-center gap-3"
    >
      <Text className="text-sm font-bold text-remetra-mauve w-6 text-center">{rank}</Text>
      <View className="flex-1">
        <Text className="text-[15px] text-neutral-700 font-semibold">{item.name}</Text>
        {subtitle ? (
          <Text className="text-xs text-remetra-muted mt-0.5">{subtitle}</Text>
        ) : null}
      </View>
      <View className="bg-remetra-peach rounded-full px-2.5 py-1 min-w-9 items-center">
        <Text className="text-sm font-bold text-remetra-rose">{item.count}</Text>
      </View>
      <Text className="text-lg text-remetra-border">›</Text>
    </TouchableOpacity>
  );
}
