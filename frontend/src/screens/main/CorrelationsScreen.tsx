import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useState } from 'react';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import { FrequencyIntensityChart } from '../../components/FrequencyIntensityChart';
import { AssociationCard, Association } from '../../components/AssociationCard';
import { useAppNavigation } from '../../navigation/hooks';

// ---------------------------------------------------------------------------
// Placeholder data — replace with algorithmStore data once API is wired
// ---------------------------------------------------------------------------

const MOCK_SYMPTOMS = [
  { id: 'sym-1', name: 'Bloating' },
  { id: 'sym-2', name: 'Cramps' },
  { id: 'sym-3', name: 'Headache' },
];

const MOCK_ASSOCIATIONS: Record<string, Association[]> = {
  'sym-1': [
    { food_name: 'Dairy',      trigger_rate: 0.78, base_rate: 0.22, exposures: 9,  average_intensity: 7.8, fishers_p_value: 0.01  },
    { food_name: 'Gluten',     trigger_rate: 0.62, base_rate: 0.28, exposures: 7,  average_intensity: 6.2, fishers_p_value: 0.04  },
    { food_name: 'Spicy Food', trigger_rate: 0.55, base_rate: 0.30, exposures: 6,  average_intensity: 5.5, fishers_p_value: 0.08  },
    { food_name: 'Alcohol',    trigger_rate: 0.40, base_rate: 0.25, exposures: 4,  average_intensity: 4.8, fishers_p_value: 0.15  },
  ],
  'sym-2': [
    { food_name: 'Dairy',  trigger_rate: 0.65, base_rate: 0.20, exposures: 6,  average_intensity: 8.1, fishers_p_value: 0.03  },
    { food_name: 'Coffee', trigger_rate: 0.50, base_rate: 0.25, exposures: 8,  average_intensity: 5.5, fishers_p_value: 0.09  },
  ],
  'sym-3': [
    { food_name: 'Alcohol', trigger_rate: 0.80, base_rate: 0.15, exposures: 5,  average_intensity: 8.5, fishers_p_value: 0.008 },
    { food_name: 'Coffee',  trigger_rate: 0.60, base_rate: 0.30, exposures: 10, average_intensity: 6.0, fishers_p_value: 0.04  },
    { food_name: 'Sugar',   trigger_rate: 0.35, base_rate: 0.20, exposures: 7,  average_intensity: 4.2, fishers_p_value: 0.18  },
  ],
};

// ---------------------------------------------------------------------------

export function CorrelationsScreen() {
  const navigation = useAppNavigation();
  const [selectedSymptomId, setSelectedSymptomId] = useState(MOCK_SYMPTOMS[0].id);

  const associations = MOCK_ASSOCIATIONS[selectedSymptomId] ?? [];
  const selectedName = MOCK_SYMPTOMS.find(s => s.id === selectedSymptomId)?.name ?? '';

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
          {MOCK_SYMPTOMS.map(symptom => (
            <TouchableOpacity
              key={symptom.id}
              onPress={() => setSelectedSymptomId(symptom.id)}
              style={{
                paddingHorizontal: 16,
                paddingVertical: 8,
                borderRadius: 20,
                backgroundColor: selectedSymptomId === symptom.id ? '#ca5e5e' : 'white',
                shadowColor: '#000',
                shadowOpacity: 0.08,
                shadowRadius: 3,
                elevation: 2,
              }}
            >
              <Text
                style={{
                  fontSize: 13,
                  fontWeight: '600',
                  color: selectedSymptomId === symptom.id ? 'white' : '#444',
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
