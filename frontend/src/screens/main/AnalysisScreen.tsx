import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useBankStore } from '../../store/bankStore';
import { symptomLogService } from '../../api/symptom_log_service';
import { algorithmService } from '../../api/algorithm_service';
import { useAuthStore } from '../../store/useAuthStore';
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

        const loggedSymptomIds = counts.map((s) => s.symptomId);
        if (loggedSymptomIds.length > 0 && username) {
          algorithmService
            .analyze({ user_id: username, symptom_ids: loggedSymptomIds })
            .catch(() => {});
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

        <SectionDivider label="Symptoms by Occurrences" />

        {loading ? (
          <ActivityIndicator color="#b2939b" style={{ marginTop: 32 }} />
        ) : error ? (
          <Text className="text-remetra-burgundy text-center mt-6">{error}</Text>
        ) : symptomCounts.length === 0 ? (
          <Text className="text-remetra-muted text-center mt-6 text-sm">
            No symptoms logged yet.
          </Text>
        ) : (
          <View className="gap-2.5">
            {symptomCounts.map((item, index) => (
              <SymptomRow key={item.symptomId} rank={index + 1} item={item} />
            ))}
          </View>
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
  const subtitle = [item.location, item.sensation].filter(Boolean).join(' · ');

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('SymptomDetail', { symptomId: item.symptomId, symptomName: item.name })}
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
