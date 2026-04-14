import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useEffect, useState } from 'react';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import { FishersExposuresChart } from '../../components/FishersExposuresChart';
import { useAppNavigation } from '../../navigation/hooks';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';
import { AssociationCard, Association } from '../../components/AssociationCard';
import { useAuthStore } from '../../store/useAuthStore';

export function CorrelationsScreen() {
  const navigation = useAppNavigation();
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, isLoading, error, fetchAssociations } = useAlgorithmStore();

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
                      <FishersExposuresChart data={associations} />
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
          )
        }
        </ScrollView>
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
                  fontFamily: undefined,
                  color: activeSymptomId === symptom.id ? 'white' : '#444',
                }}
              >
                {symptom.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Main content */}
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
