
import { View, Button, Text, TouchableOpacity } from 'react-native';
import { useState } from 'react';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import LogEntryModal from '../../components/LogEntryModal'
import { useAuthStore } from '../../store/useAuthStore';
import { useAppNavigation } from '../../navigation/hooks';

// Placeholder — replace with top associations from algorithmStore once API is wired
const SUMMARY_PLACEHOLDER = {
  symptomName: 'bloating',
  foodName: 'dairy',
  exposures: 7,
  totalOccurrences: 10,
  chartData: [
    { food_name: 'Dairy',      trigger_rate: 0.78 },
    { food_name: 'Gluten',     trigger_rate: 0.62 },
    { food_name: 'Spicy Food', trigger_rate: 0.55 },
    { food_name: 'Alcohol',    trigger_rate: 0.40 },
  ],
};

export function SummaryScreen() {
  const navigation = useAppNavigation();
  const { logout } = useAuthStore()

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
      <View className="flex-1 p-6">
        <Text className="text-[28px] font-semibold text-center text-[#b2939b] italic">
          YOUR SUMMARY
        </Text>
        <Text className="text-center text-black my-[10%] text-lg">
          {GetPersonalizedIntro(
            useAuthStore.getState().user.name ?? 'there',
            SUMMARY_PLACEHOLDER.symptomName,
            SUMMARY_PLACEHOLDER.foodName,
            SUMMARY_PLACEHOLDER.exposures,
            SUMMARY_PLACEHOLDER.totalOccurrences,
          )}
        </Text>

        <TriggerRateChart data={SUMMARY_PLACEHOLDER.chartData} />

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
      </View>
    </View>
  );
}

function GetPersonalizedIntro(name: string, symptom: string, food: string, numerator: number, denominator: number) {
  return `${name}, in the last 7 days, your ${symptom} has correlated with eating ${food} ${numerator}/${denominator} times.`
}