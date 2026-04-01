
import { View, Button, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useState, useEffect } from 'react';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import LogEntryModal from '../../components/LogEntryModal'
import { useAuthStore } from '../../store/useAuthStore';
import { useAppNavigation } from '../../navigation/hooks';
import { useAlgorithmStore } from '../../store/useAlgorithmStore';

export function SummaryScreen() {
  const navigation = useAppNavigation();
  const { logout } = useAuthStore();
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, fetchAssociations } = useAlgorithmStore();

  useEffect(() => {
    if (userId) fetchAssociations(userId);
  }, [userId]);

  // Find top association across all symptoms by trigger_rate
  const allAssociations = Object.values(associationsBySymptom).flat();
  const topAssoc = allAssociations.sort((a, b) => b.trigger_rate - a.trigger_rate)[0] ?? null;
  const topSymptom = topAssoc ? (symptoms.find(s => s.id === topAssoc.symptom_id)?.name ?? '') : '';

  // Chart data: top associations for the symptom of the top association, or all top entries
  const topSymptomId = topAssoc?.symptom_id ?? null;
  const chartData = (topSymptomId ? (associationsBySymptom[topSymptomId] ?? []) : allAssociations)
    .slice()
    .sort((a, b) => b.trigger_rate - a.trigger_rate)
    .slice(0, 5)
    .map(a => ({ food_name: a.food_name, trigger_rate: a.trigger_rate }));

  const [showModal, setShowModal] = useState(false);

  return (
    <View className="flex-1 relative">
      <LogEntryModal
          visible={showModal}
          onClose={() => setShowModal(false)}
          onLogEntry={(entry) => {
            // persist the entry?
          }}
      />
      <BackgroundGradient />
      <ScrollView className="flex-1" contentContainerStyle={{ padding: 24, paddingBottom: 48 }}>
        <Text className="text-[28px] font-semibold text-center text-[#b2939b] italic">
          YOUR SUMMARY
        </Text>
        <Text className="text-center text-black my-[10%] text-lg">
          {topAssoc
            ? GetPersonalizedIntro(
                useAuthStore.getState().user.name ?? 'there',
                topSymptom,
                topAssoc.food_name,
                topAssoc.exposures,
                allAssociations.length,
              )
            : `${useAuthStore.getState().user.name ?? 'there'}, no associations found yet. Log some meals and symptoms to get started.`}
        </Text>

        <TriggerRateChart data={chartData} />

        <View className="m-[10%]">
          <Button
            color="#ca5e5e"
            title="VIEW ALL CORRELATIONS -->"
            onPress={() => navigation.navigate('Correlations')}
          />
        </View>
        
        <View className="m-[10%]">
          <TouchableOpacity
            style={{
              paddingVertical: 16,
              paddingHorizontal: 32,
              borderRadius: 50,
              backgroundColor: '#B8624F',
              alignItems: 'center',
              justifyContent: 'center',
              shadowColor: '#000',
              shadowOpacity: 0.2,
              shadowRadius: 4,
              shadowOffset: { width: 0, height: 2 },
              elevation: 4,
            }}
            onPress={() => (
              setShowModal(true)
            )} 
          >
            <Text style={{ color: 'white', fontSize: 18, fontFamily: 'PTSerif' }}>+ Add Log</Text>
          </TouchableOpacity>
        </View>
        <View className="flex-row justify-between m-[3%] gap-2">
          <TouchableOpacity
            className="flex-1 bg-[#ca5e5e] rounded-md py-2 px-1"
            onPress={logout}
          >
            <Text className="text-white text-center text-xs font-semibold">LOGOUT</Text>
          </TouchableOpacity>

          <TouchableOpacity
            className="flex-1 bg-[#ca5e5e] rounded-md py-2 px-1"
            onPress={() => {
              useAuthStore.setState({ hasCompletedOnboarding: false });
              logout();
            }}
          >
            <Text className="text-white text-center text-xs font-semibold">LOGOUT + RESET</Text>
          </TouchableOpacity>

          <TouchableOpacity
            className="flex-1 bg-[#ca5e5e] rounded-md py-2 px-1"
            onPress={() => useAuthStore.setState({ hasCompletedOnboarding: false })}
          >
            <Text className="text-white text-center text-xs font-semibold">RESET ONBOARD</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

function GetPersonalizedIntro(name: string, symptom: string, food: string, numerator: number, denominator: number) {
  return `${name}, in the last 7 days, your ${symptom} has correlated with eating ${food} ${numerator}/${denominator} times.`
}