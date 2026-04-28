import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useState } from 'react';
import { useAppNavigation } from '../../navigation/hooks';
import { useFonts } from 'expo-font';
import { Lora_400Regular } from '@expo-google-fonts/lora';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';


const GOAL_OPTIONS = [
  'Track symptoms related to autoimmune disease',
  'Identify trigger ingredients',
  'Discover correlations between current habits',
  'Improve quality of life through informed changes',
];

export function UserGoalsScreen() {
  const navigation = useAppNavigation();
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const [fontsLoaded] = useFonts({
    Lora_400Regular,
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null; 
  }

  const toggleGoal = (goal: string) => {
    if (selectedGoals.includes(goal)) {
      setSelectedGoals(selectedGoals.filter(g => g !== goal));
    } else {
      setSelectedGoals([...selectedGoals, goal]);
    }
  };

  const handleDone = () => {
    navigation.navigate('SymptomFoodBank'); 
  };

 return (
    <View className="flex-1">
      <BackgroundGradient />

      <ScrollView 
        contentContainerClassName="flex-grow px-6 pt-[60px] pb-10"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-1">
          <Text className="text-xl text-remetra-espresso font-ptserif text-center mt-36 mb-2 font-normal">
            What Are You Hoping To Accomplish With Remetra?
          </Text>
          <Text className="text-base text-remetra-warm-brown font-ptserif text-center mb-8 opacity-80">
            Select all that apply
          </Text>

          <View className="gap-5 mb-10">
            {GOAL_OPTIONS.map((goal) => (
              <TouchableOpacity
                key={goal}
                className={`rounded-xl overflow-hidden shadow-md ${selectedGoals.includes(goal) ? 'bg-remetra-burgundy' : 'bg-remetra-coral'}`}
                onPress={() => toggleGoal(goal)}
                activeOpacity={0.7}
              >
                <View className="py-6 px-6 items-center">
                  <Text className="text-white text-base font-ptserif font-medium text-center leading-5">
                    {goal}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
          
        </View>
      </ScrollView>

      {/* Sticky CTA */}
      <View className="px-6 pb-12">
        <TouchableOpacity 
          className="bg-remetra-burgundy py-4 rounded-[25px] items-center shadow-md mt-auto"
          onPress={handleDone}
        >
          <Text className="text-white font-ptserif text-lg font-semibold">
            Next
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

}