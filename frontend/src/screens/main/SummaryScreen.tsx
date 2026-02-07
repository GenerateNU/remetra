
import { View, Button, Text } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { GenericCorrelationChart } from '../../components/GenericCorrelationChart'
import { useAppNavigation } from '../../navigation/hooks';

export function SummaryScreen() {
  const navigation = useAppNavigation();

  return (
    <View className="flex-1 relative">
      <BackgroundGradient />
      
      <View className="flex-1 p-6">
        <Text className="text-[28px] font-semibold text-center text-[#b2939b] italic">
          YOUR SUMMARY
        </Text>
        
        <Text className="text-center text-black my-[10%] text-lg">
          {GetPersonalizedIntro("Nicole", "stomache pain", "pizza", 5, 10)}
        </Text>
        
        <GenericCorrelationChart />

        <View className="m-[10%]">
          <Button 
            color="#ca5e5e" 
            title="VIEW ALL CORRELATIONS -->" 
            onPress={() => {}} 
          />
        </View>
        
        <View className="m-[10%]">
          <Button 
            color="#ca5e5e" 
            title="+ Add Data" 
            onPress={() => {}} 
          />
        </View>
      </View>
    </View>
  );
}

function GetPersonalizedIntro(name: string, symptom: string, food: string, numerator: number, denominator: number) {
  return `${name}, in the last 7 days, your ${symptom} has correlated with eating ${food} ${numerator}/${denominator} times.`
}