import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useState } from 'react';
import { useAppNavigation } from '../../navigation/hooks';
import { useFonts } from 'expo-font';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { ItemBank } from '../../components/ItemBank';

interface Symptom {
  name: string;
}

interface Food {
  name: string;
}

export function SymptomFoodBankScreen() {
  const navigation = useAppNavigation();
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [foods, setFoods] = useState<Food[]>([]);

  const [fontsLoaded] = useFonts({
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null;
  }

  const removeSymptom = (name: string) => {
    setSymptoms(symptoms.filter(s => s.name !== name));
  };

  const removeFood = (name: string) => {
    setFoods(foods.filter(f => f.name !== name));
  };

  const handleDone = () => {
    navigation.navigate('Summary');
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
          <Text className="text-[32px] font-light font-ptserif tracking-[3px] text-[#eea487]">
            R E M E T R A
          </Text>
        </View>

        <ItemBank
          title="Enter any symptoms you typically experience."
          subtitle="Use the dropdown or enter in your own words."
          description={`You can always add and modify these later.\nBe as specific as possible for improved personalization.`}
          items={symptoms}
          emptyMessage="No symptoms added yet"
          onRemove={removeSymptom}
          onAdd={() => {
            // TODO: Open add symptom popup component
          }}
        />

        <ItemBank
          title="Enter any foods you eat regularly."
          subtitle={`Use the dropdown, scan typical food items,\nor enter manually.`}
          description={`You can also add as you go.\nAs you use Remetra more, repeat items will populate automatically.`}
          items={foods}
          emptyMessage="No foods added yet"
          onRemove={removeFood}
          onAdd={() => {
            // TODO: Open add food popup component
          }}
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
