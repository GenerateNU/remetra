import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  useWindowDimensions,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { VictoryBar, VictoryChart, VictoryAxis, VictoryTheme } from 'victory-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { algorithmService, AlgorithmAssociationResponse } from '../../api/algorithm_service';
import { useBankStore } from '../../store/bankStore';
import { useAuthStore } from '../../store/useAuthStore';
import { MainStackParamList } from '../../navigation/stacks/MainStack';

type Props = NativeStackScreenProps<MainStackParamList, 'SymptomDetail'>;

interface FoodCorrelation {
  foodId: string;
  name: string;
  ingredients: string[];
  triggerRate: number;
}

interface IngredientCorrelation {
  name: string;
  triggerRate: number;
}

const CHART_LIMIT = 5;

export function SymptomDetailScreen({ route, navigation }: Props) {
  const { symptomId, symptomName } = route.params;
  const { width: screenWidth } = useWindowDimensions();
  const { fetchFoods } = useBankStore();
  const username = useAuthStore((s) => s.user.name);
  const [correlations, setCorrelations] = useState<FoodCorrelation[]>([]);
  const [ingredientCorrelations, setIngredientCorrelations] = useState<IngredientCorrelation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        await fetchFoods();
        const results: AlgorithmAssociationResponse[] = await algorithmService.getAssociations(
          username!,
          symptomId
        );

        const foodMap = new Map(
          useBankStore.getState().foods.map((f) => [f.id, f.name])
        );

        const mapped: FoodCorrelation[] = results
          .map((r) => ({
            foodId: r.associated_food_id,
            name: foodMap.get(r.associated_food_id) ?? `Food ${r.associated_food_id}`,
            ingredients: r.ingredients,
            triggerRate: r.key_metrics.trigger_rate,
          }))
          .sort((a, b) => b.triggerRate - a.triggerRate);

        setCorrelations(mapped);

        const ingMap = new Map<string, number>();
        for (const food of mapped) {
          for (const ing of food.ingredients) {
            ingMap.set(ing, Math.max(ingMap.get(ing) ?? 0, food.triggerRate));
          }
        }
        const ingList: IngredientCorrelation[] = Array.from(ingMap.entries())
          .map(([name, triggerRate]) => ({ name, triggerRate }))
          .sort((a, b) => b.triggerRate - a.triggerRate);
        setIngredientCorrelations(ingList);
      } catch (err: any) {
        setError(err.message ?? 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const chartData = ingredientCorrelations.slice(0, CHART_LIMIT).map((c) => ({
    x: c.name.length > 10 ? c.name.slice(0, 9) + '…' : c.name,
    y: c.triggerRate,
  }));

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>

        {/* Back button */}
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          className="flex-row items-center mb-6 gap-1.5"
        >
          <Text className="text-lg text-remetra-mauve">‹</Text>
          <Text className="text-sm text-remetra-mauve">Analysis</Text>
        </TouchableOpacity>

        {/* Title */}
        <Text className="text-2xl font-semibold text-remetra-mauve italic tracking-[1px] text-center mb-8">
          {symptomName.toUpperCase()}
        </Text>

        {loading ? (
          <ActivityIndicator color="#b2939b" style={{ marginTop: 32 }} />
        ) : error ? (
          <Text className="text-remetra-burgundy text-center mt-6">{error}</Text>
        ) : ingredientCorrelations.length === 0 ? (
          <Text className="text-remetra-muted text-center mt-6 text-sm">
            No correlation data yet. Log more food and symptoms to see results.
          </Text>
        ) : (
          <>
            {/* Chart */}
            <View className="bg-white/35 rounded-2xl p-2 mb-8">
              <Text className="text-[13px] font-bold text-remetra-muted tracking-[1px] text-center mb-1">
                TOP INGREDIENT CORRELATIONS
              </Text>
              <VictoryChart
                theme={VictoryTheme.material}
                domainPadding={20}
                width={screenWidth - 64}
                height={220}
                padding={{ top: 16, bottom: 48, left: 40, right: 16 }}
              >
                <VictoryAxis
                  style={{ tickLabels: { fontSize: 9, fill: '#666' }, grid: { stroke: 'none' } }}
                />
                <VictoryAxis
                  dependentAxis
                  tickFormat={(t: number) => `${Math.round(t * 100)}%`}
                  style={{ tickLabels: { fontSize: 9, fill: '#666' }, grid: { stroke: '#eee' } }}
                />
                <VictoryBar
                  data={chartData}
                  style={{ data: { fill: '#F8B4A8' } /* remetra-peach */ }}
                  cornerRadius={4}
                />
              </VictoryChart>
            </View>

            {/* List */}
            <SectionDivider label="Related Ingredients" />
            <View className="gap-2.5">
              {ingredientCorrelations.map((item, index) => (
                <IngredientRow key={item.name} rank={index + 1} item={item} />
              ))}
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View className="flex-row items-center mb-3">
      <Text className="text-xs font-bold text-remetra-muted mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-neutral-200" />
    </View>
  );
}

function IngredientRow({ rank, item }: { rank: number; item: IngredientCorrelation }) {
  const pct = Math.round(item.triggerRate * 100);
  // Bar colour driven by trigger rate — full class names required for Tailwind purge
  const barCls = pct >= 60 ? 'bg-remetra-burgundy' : pct >= 30 ? 'bg-remetra-peach' : 'bg-green-200';

  return (
    <View className="bg-white/35 rounded-xl p-4 gap-2">
      <View className="flex-row items-center gap-3">
        <Text className="text-sm font-bold text-remetra-mauve w-6 text-center">{rank}</Text>
        <Text className="text-[15px] text-neutral-700 font-semibold flex-1">{item.name}</Text>
        <Text className="text-sm font-bold text-remetra-rose">{pct}%</Text>
      </View>

      {/* Trigger rate bar */}
      <View className="h-1.5 bg-neutral-200 rounded-full ml-9">
        <View
          className={`h-1.5 rounded-full ${barCls}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </View>
    </View>
  );
}
