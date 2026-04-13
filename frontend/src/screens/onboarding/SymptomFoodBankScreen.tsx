import { View, Text, TouchableOpacity, ScrollView} from 'react-native';
import { useState, useEffect } from 'react';
import { useFonts } from 'expo-font';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { ItemBank } from '../../components/ItemBank';
import { AddSymptomModal } from '../../components/AddSymptomModal';
import { AddFoodModal } from '../../components/AddFoodModal';
import { useBankStore } from '../../store/bankStore';
import { useAuthStore } from '../../store/useAuthStore';

export function SymptomFoodBankScreen() {
  const { completeOnboarding } = useAuthStore()

  const { foods, symptoms, removeFood, removeSymptom, fetchFoods, fetchSymptoms } = useBankStore();
  const [showSymptomModal, setShowSymptomModal] = useState(false);
  const [showFoodModal, setShowFoodModal] = useState(false);

  useEffect(() => {
    fetchFoods();
    fetchSymptoms();
  }, []);

  const [fontsLoaded] = useFonts({
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null;
  }

  const handleDone = () => {
    completeOnboarding()
  };

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView
        contentContainerClassName="flex-grow px-6 pt-[60px] pb-10"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="items-center mb-8">
          <Text className="text-brand font-light font-ptserif tracking-[3px] text-remetra-accent">
            R E M E T R A
          </Text>
        </View>

        <ItemBank
          title="Build your symptom bank."
          subtitle={`Describe Symptoms you experience regularily, breaking them down by location and sensation`}
          description="Be as specific as possible. You can always add or edit these later."
          items={symptoms}
          emptyMessage="No symptoms added yet"
          onRemove={removeSymptom}
          onAdd={() => setShowSymptomModal(true)}
        />

        <AddSymptomModal
          visible={showSymptomModal}
          onClose={() => setShowSymptomModal(false)}
        />

        <ItemBank
          title="Build your food bank."
          subtitle={`Add foods you eat regularly with their key ingredients.\ne.g. Greek Yogurt → milk, live cultures`}
          description="You can add more as you go — Remetra learns as you log."
          items={foods}
          emptyMessage="No foods added yet"
          onRemove={removeFood}
          onAdd={() => setShowFoodModal(true)}
        />

        <AddFoodModal
          visible={showFoodModal}
          onClose={() => setShowFoodModal(false)}
        />

        {/* Done Button */}
        <TouchableOpacity
          className="bg-white py-4 rounded-[25px] items-center shadow-md mt-auto"
          onPress={handleDone}
        >
          <Text className="text-remetra-rose font-ptserif text-lg font-semibold">
            Done
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
