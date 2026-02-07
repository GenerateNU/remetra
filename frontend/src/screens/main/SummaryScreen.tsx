
import { View, Button, Text } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useAppNavigation } from '../../navigation/hooks';
import {VictoryBar, VictoryChart, VictoryTheme, VictoryAxis } from 'victory-native';

function GenericCorrelationChart() {
  const data = [
    { food: 'Pizza', correlation: 0.7 },
    { food: 'Dairy', correlation: 0.4 },
    { food: 'Spicy', correlation: 0.6 },
    { food: 'Sugar', correlation: 0.2 },
  ];

  return (
    <View className="bg-white rounded-2xl p-4 my-4">
      <Text className="text-center text-lg font-semibold mb-2">
        Top Food Correlations
      </Text>

      <VictoryChart
        theme={VictoryTheme.material}
        domainPadding={20}
        height={220}
      >
        <VictoryAxis
          tickFormat={data.map(d => d.food)}
          style={{
            tickLabels: { fontSize: 10 },
          }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(t: number) => `${Math.round(t * 100)}%`}
        />

        <VictoryBar
          data={data}
          x="food"
          y="correlation"
          style={{
            data: { fill: '#ca5e5e' },
          }}
          cornerRadius={4}
        />
      </VictoryChart>
    </View>
  );
}

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