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

  // navigate to the final onboarding screen here, replace name? 
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
        <View className="items-center mb-10">
          <Text className="text-[32px] font-light font-ptserif tracking-[3px] text-[#eea487]">
            R E M E T R A
          </Text>
        </View>

        <View className="flex-1">
          <Text className="text-xl text-[#C85A4A] font-ptserif text-center mb-2 font-normal">
            What are you hoping to accomplish with Remetra?
          </Text>
          <Text className="text-base text-[#C85A4A] font-ptserif text-center mb-8 opacity-80">
            Select all that apply
          </Text>

          <View className="gap-5 mb-10">
            {GOAL_OPTIONS.map((goal) => (
              <TouchableOpacity
                key={goal}
                className={`py-6 px-6 rounded-xl items-center shadow-md ${
                  selectedGoals.includes(goal)
                    ? 'bg-[#B8624F] border-2 border-white'
                    : 'bg-[#D9806E]'
                }`}
                onPress={() => toggleGoal(goal)}
                activeOpacity={0.7}
              >
                <Text className="text-white text-[16px] font-ptserif font-medium text-center leading-5">
                  {goal}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity 
            className="bg-white py-4 rounded-[25px] items-center shadow-md mt-auto"
            onPress={handleDone}
          >
            <Text className="text-[#C85A4A] font-ptserif text-lg font-semibold">
              Done
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );

}