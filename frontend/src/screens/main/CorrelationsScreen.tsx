import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, TextInput } from 'react-native';
import { useEffect, useMemo, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { FishersExposuresChart } from '../../components/FishersExposuresChart';
import { useAlgorithmStore, EnrichedAssociation } from '../../store/useAlgorithmStore';
import { AssociationCard } from '../../components/AssociationCard';
import { useAuthStore } from '../../store/useAuthStore';
import { MainStackParamList } from '../../navigation/stacks/MainStack';

type Props = NativeStackScreenProps<MainStackParamList, 'Correlations'>;

export function CorrelationsScreen({ navigation, route }: Props) {
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, isLoading, error, fetchAssociations, minExposures, setMinExposures } = useAlgorithmStore();

  useEffect(() => {
    if (userId) fetchAssociations(userId);
  }, [userId]);
  const [selectedSymptomId, setSelectedSymptomId] = useState<string | null>(
    route.params?.initialSymptomId ?? null
  );

  const hasData = symptoms.length > 0;

  const filteredBySymptom = useMemo(() => {
    const result: Record<string, EnrichedAssociation[]> = {};
    for (const [symptomId, assocs] of Object.entries(associationsBySymptom)) {
      const filtered = assocs.filter(a => a.exposures >= minExposures);
      if (filtered.length > 0) result[symptomId] = filtered;
    }
    return result;
  }, [associationsBySymptom, minExposures]);

  const filteredSymptoms = symptoms.filter(s => filteredBySymptom[s.id]);

  const activeSymptomId = selectedSymptomId ?? filteredSymptoms[0]?.id ?? null;
  const activeAssociations = activeSymptomId
    ? (filteredBySymptom[activeSymptomId] ?? []).slice().sort((a, b) => b.trigger_rate - a.trigger_rate)
    : [];
  const activeName = symptoms.find(s => s.id === activeSymptomId)?.name ?? '';

  const topTriggers = useMemo(() => {
    const best: Record<string, (typeof activeAssociations)[number] & { symptom_name: string }> = {};
    for (const symptom of symptoms) {
      const assocs = (filteredBySymptom[symptom.id] ?? []);
      for (const assoc of assocs) {
        const excessRisk = assoc.trigger_rate - assoc.base_rate;
        const bestExcessRisk = best[assoc.ingredient_name]
          ? best[assoc.ingredient_name].trigger_rate - best[assoc.ingredient_name].base_rate
          : -Infinity;
        if (excessRisk > bestExcessRisk) {
          best[assoc.ingredient_name] = { ...assoc, symptom_name: symptom.name };
        }
      }
    }
    return Object.values(best)
      .filter(a => a.trigger_rate > a.base_rate)
      .sort((a, b) => (b.trigger_rate - b.base_rate) - (a.trigger_rate - a.base_rate))
      .slice(0, 5);
  }, [filteredBySymptom, symptoms]);

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
          ) : !hasData ? (
            <Text style={{ textAlign: 'center', color: '#888', marginTop: 40 }}>
              No correlation data yet. Log more food and symptoms to see results.
            </Text>
          ) : (
            <>
              {/* Min exposures filter */}
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 16, gap: 8 }}>
                <Text style={{ fontSize: 13, color: '#888' }}>Min exposures:</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                  <TouchableOpacity
                    onPress={() => setMinExposures(minExposures - 1)}
                    style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <Text style={{ fontSize: 18, fontWeight: '600', color: '#666' }}>-</Text>
                  </TouchableOpacity>
                  <TextInput
                    value={String(minExposures)}
                    onChangeText={text => {
                      const n = parseInt(text, 10);
                      if (!isNaN(n) && n >= 1) setMinExposures(n);
                    }}
                    keyboardType="number-pad"
                    style={{
                      width: 48,
                      height: 32,
                      textAlign: 'center',
                      fontSize: 15,
                      fontWeight: '600',
                      color: '#333',
                      backgroundColor: 'white',
                      borderRadius: 8,
                      borderWidth: 1,
                      borderColor: '#ddd',
                    }}
                  />
                  {filteredSymptoms.length === 0 ?(
                    <></>
                  ) : (
                    <TouchableOpacity
                      onPress={() => setMinExposures(minExposures + 1)}
                      style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0', alignItems: 'center', justifyContent: 'center' }}
                    >
                      <Text style={{ fontSize: 18, fontWeight: '600', color: '#666' }}>+</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>

              {filteredSymptoms.length === 0 ? (
                <Text style={{ textAlign: 'center', color: '#888', marginTop: 20 }}>
                  No correlations with {minExposures}+ exposures. Try lowering the minimum.
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
                    <AssociationCard key={assoc.ingredient_name} {...assoc} />
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
                    data={activeAssociations.map(a => ({ ingredient_name: a.ingredient_name, trigger_rate: a.trigger_rate }))}
                    title={`${activeName} — Trigger Rates`}
                  /> */}
                  <FishersExposuresChart data={activeAssociations} />
                  {/* <FrequencyIntensityChart
                    data={activeAssociations.map(a => ({
                      ingredient_name: a.ingredient_name,
                      exposures: a.exposures,
                      average_intensity: a.average_intensity,
                    }))}
                  /> */}
                  {/* <Text style={{ fontSize: 15, fontWeight: '600', marginTop: 8, marginBottom: 4, color: '#333' }}>
                    Breakdown
                  </Text>
                  {activeAssociations.map(assoc => (
                    <AssociationCard key={assoc.ingredient_name} {...assoc} />
                  ))} */}
                </View>
              )}
              </>
              )}
            </>
          )}
        </ScrollView>
      </View>
    </View>
  );
}
