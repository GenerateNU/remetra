import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useEffect, useMemo, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import { FishersExposuresChart } from '../../components/FishersExposuresChart';
import { FrequencyIntensityChart } from '../../components/FrequencyIntensityChart';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';
import { AssociationCard } from '../../components/AssociationCard';
import { useAuthStore } from '../../store/useAuthStore';
import { MainStackParamList } from '../../navigation/stacks/MainStack';

type Props = NativeStackScreenProps<MainStackParamList, 'Correlations'>;

export function CorrelationsScreen({ navigation, route }: Props) {
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, isLoading, error, fetchAssociations } = useAlgorithmStore();

  useEffect(() => {
    if (userId) fetchAssociations(userId);
  }, [userId]);
  const [selectedSymptomId, setSelectedSymptomId] = useState<string | null>(
    route.params?.initialSymptomId ?? null
  );

  const activeSymptomId = selectedSymptomId ?? symptoms[0]?.id ?? null;
  const activeAssociations = activeSymptomId
    ? (associationsBySymptom[activeSymptomId] ?? []).slice().sort((a, b) => b.trigger_rate - a.trigger_rate)
    : [];
  const activeName = symptoms.find(s => s.id === activeSymptomId)?.name ?? '';

  const topTriggers = useMemo(() => {
    const best: Record<string, (typeof activeAssociations)[number] & { symptom_name: string }> = {};
    for (const symptom of symptoms) {
      const assocs = associationsBySymptom[symptom.id] ?? [];
      for (const assoc of assocs) {
        if (!best[assoc.food_name] || assoc.trigger_rate > best[assoc.food_name].trigger_rate) {
          best[assoc.food_name] = { ...assoc, symptom_name: symptom.name };
        }
      }
    }
    return Object.values(best)
      .sort((a, b) => b.trigger_rate - a.trigger_rate)
      .slice(0, 5);
  }, [associationsBySymptom, symptoms]);

  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <View style={{ flex: 1 }}>
        {/* Header */}
        <View style={{ paddingTop: 56, paddingHorizontal: 24, paddingBottom: 8 }}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginBottom: 8 }}>
            <Text style={{ color: '#ca5e5e', fontSize: 14 }}>← Back</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 24, fontWeight: '600', color: '#b2939b', fontStyle: 'italic', textAlign: 'center' }}>
            {activeName}
          </Text>
        </View>

        {/* Main content */}
        <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 32 }}>
          {isLoading ? (
            <ActivityIndicator color="#b2939b" style={{ marginTop: 48 }} />
          ) : error ? (
            <Text style={{ textAlign: 'center', color: '#ca5e5e', marginTop: 40 }}>{error}</Text>
          ) : symptoms.length === 0 ? (
            <Text style={{ textAlign: 'center', color: '#888', marginTop: 40 }}>
              No correlation data yet. Log more food and symptoms to see results.
            </Text>
          ) : (
            <>
              {/* Top triggers across all symptoms */}
              {topTriggers.length > 0 && (
                <View style={{ marginBottom: 32 }}>
                  <Text style={{ fontSize: 18, fontWeight: '700', color: '#b2939b', marginBottom: 4 }}>
                    Top Triggers
                  </Text>
                  <Text style={{ fontSize: 12, color: '#999', marginBottom: 12 }}>
                    Highest correlated ingredients across all symptoms
                  </Text>
                  {topTriggers.map(assoc => (
                    <AssociationCard key={assoc.food_name} {...assoc} />
                  ))}
                </View>
              )}

              {/* Per-symptom detail */}
              {activeAssociations.length === 0 ? (
                <Text style={{ color: '#888', textAlign: 'center' }}>
                  No correlations found for {activeName}.
                </Text>
              ) : (
                <View style={{ marginBottom: 40 }}>
                  <Text style={{ fontSize: 18, fontWeight: '700', color: '#b2939b', marginBottom: 12 }}>
                    Overview
                  </Text>
                  {/* <TriggerRateChart
                    data={activeAssociations.map(a => ({ food_name: a.food_name, trigger_rate: a.trigger_rate }))}
                    title={`${activeName} — Trigger Rates`}
                  /> */}
                  <FishersExposuresChart data={activeAssociations} />
                  {/* <FrequencyIntensityChart
                    data={activeAssociations.map(a => ({
                      food_name: a.food_name,
                      exposures: a.exposures,
                      average_intensity: a.average_intensity,
                    }))}
                  /> */}
                  {/* <Text style={{ fontSize: 15, fontWeight: '600', marginTop: 8, marginBottom: 4, color: '#333' }}>
                    Breakdown
                  </Text>
                  {activeAssociations.map(assoc => (
                    <AssociationCard key={assoc.food_name} {...assoc} />
                  ))} */}
                </View>
              )}
            </>
          )}
        </ScrollView>
      </View>
    </View>
  );
}
