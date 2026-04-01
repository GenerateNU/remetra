import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useState, useEffect } from 'react';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import { FrequencyIntensityChart } from '../../components/FrequencyIntensityChart';
import { AssociationCard } from '../../components/AssociationCard';
import { useAppNavigation } from '../../navigation/hooks';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';
import { useAuthStore } from '../../store/useAuthStore';

export function CorrelationsScreen() {
  const navigation = useAppNavigation();
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, fetchAssociations } = useAlgorithmStore();

  useEffect(() => {
    if (userId) fetchAssociations(userId);
  }, [userId]);

  const [selectedSymptomId, setSelectedSymptomId] = useState<string | null>(null);

  const activeSymptomId = selectedSymptomId ?? symptoms[0]?.id ?? null;
  const associations = activeSymptomId ? (associationsBySymptom[activeSymptomId] ?? []) : [];
  const selectedName = symptoms.find(s => s.id === activeSymptomId)?.name ?? '';

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
            ALL CORRELATIONS
          </Text>
        </View>

        {/* Symptom selector */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ paddingHorizontal: 16, paddingVertical: 12, gap: 8 }}
        >
          {symptoms.map(symptom => (
            <TouchableOpacity
              key={symptom.id}
              onPress={() => setSelectedSymptomId(symptom.id)}
              style={{
                paddingHorizontal: 16,
                paddingVertical: 8,
                borderRadius: 20,
                backgroundColor: activeSymptomId === symptom.id ? '#ca5e5e' : 'white',
                shadowColor: '#000',
                shadowOpacity: 0.08,
                shadowRadius: 3,
                elevation: 2,
              }}
            >
              <Text
                numberOfLines={1}
                style={{
                  fontSize: 13,
                  fontWeight: '600',
                  color: activeSymptomId === symptom.id ? 'white' : '#444',
                  includeFontPadding: false,
                }}
              >
                {symptom.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Main content */}
        <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 32 }}>
          {associations.length === 0 ? (
            <Text style={{ textAlign: 'center', color: '#888', marginTop: 40 }}>
              No correlations found for {selectedName}.
            </Text>
          ) : (
            <>
              {/* Chart 1: Trigger rate bar */}
              <TriggerRateChart
                data={associations.map(a => ({ food_name: a.food_name, trigger_rate: a.trigger_rate }))}
                title={`${selectedName} — Trigger Rates`}
              />

              {/* Chart 2: Frequency vs intensity scatter */}
              <FrequencyIntensityChart
                data={associations.map(a => ({
                  food_name: a.food_name,
                  exposures: a.exposures,
                  average_intensity: a.average_intensity,
                }))}
              />

              {/* Detail cards */}
              <Text style={{ fontSize: 15, fontWeight: '600', marginTop: 8, marginBottom: 4, color: '#333' }}>
                Breakdown
              </Text>
              {associations
                .slice()
                .sort((a, b) => b.trigger_rate - a.trigger_rate)
                .map(assoc => (
                  <AssociationCard key={assoc.food_name} {...assoc} />
                ))}
            </>
          )}
        </ScrollView>
      </View>
    </View>
  );
}
