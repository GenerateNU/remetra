import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useEffect } from 'react';
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

        <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 32 }}>
          {symptoms.length === 0 ? (
            <Text style={{ textAlign: 'center', color: '#888', marginTop: 40 }}>
              No symptoms found. Log some symptoms to get started.
            </Text>
          ) : (
            symptoms.map(symptom => {
              const associations = (associationsBySymptom[symptom.id] ?? [])
                .slice()
                .sort((a, b) => b.trigger_rate - a.trigger_rate);

              return (
                <View key={symptom.id} style={{ marginBottom: 40 }}>
                  <Text style={{ fontSize: 18, fontWeight: '700', color: '#b2939b', marginBottom: 12 }}>
                    {symptom.name}
                  </Text>

                  {associations.length === 0 ? (
                    <Text style={{ color: '#888' }}>No correlations found for {symptom.name}.</Text>
                  ) : (
                    <>
                      <TriggerRateChart
                        data={associations.map(a => ({ food_name: a.food_name, trigger_rate: a.trigger_rate }))}
                        title={`${symptom.name} — Trigger Rates`}
                      />
                      <FrequencyIntensityChart
                        data={associations.map(a => ({
                          food_name: a.food_name,
                          exposures: a.exposures,
                          average_intensity: a.average_intensity,
                        }))}
                      />
                      <Text style={{ fontSize: 15, fontWeight: '600', marginTop: 8, marginBottom: 4, color: '#333' }}>
                        Breakdown
                      </Text>
                      {associations.map(assoc => (
                        <AssociationCard key={assoc.food_name} {...assoc} />
                      ))}
                    </>
                  )}
                </View>
              );
            })
          )}
        </ScrollView>
      </View>
    </View>
  );
}
