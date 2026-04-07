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
        const results: AlgorithmAssociationResponse[] = await algorithmService.getCorrelations(
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

        // Flatten to ingredient level, keeping the highest trigger rate per ingredient
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
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>

        {/* Back button */}
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 24, gap: 6 }}
        >
          <Text style={{ fontSize: 18, color: '#b2939b' }}>‹</Text>
          <Text style={{ fontSize: 14, color: '#b2939b' }}>Analysis</Text>
        </TouchableOpacity>

        {/* Title */}
        <Text
          style={{
            fontSize: 24,
            fontWeight: '600',
            color: '#b2939b',
            fontStyle: 'italic',
            letterSpacing: 1,
            textAlign: 'center',
            marginBottom: 32,
          }}
        >
          {symptomName.toUpperCase()}
        </Text>

        {loading ? (
          <ActivityIndicator color="#b2939b" style={{ marginTop: 32 }} />
        ) : error ? (
          <Text style={{ color: '#B8624F', textAlign: 'center', marginTop: 24 }}>{error}</Text>
        ) : ingredientCorrelations.length === 0 ? (
          <Text style={{ color: '#aaa', textAlign: 'center', marginTop: 24, fontSize: 14 }}>
            No correlation data yet. Log more food and symptoms to see results.
          </Text>
        ) : (
          <>
            {/* Chart */}
            <View
              style={{
                backgroundColor: 'rgba(255,255,255,0.35)',
                borderRadius: 16,
                padding: 8,
                marginBottom: 32,
              }}
            >
              <Text
                style={{
                  fontSize: 13,
                  fontWeight: '700',
                  color: '#aaa',
                  letterSpacing: 1,
                  textAlign: 'center',
                  marginBottom: 4,
                }}
              >
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
                  style={{ data: { fill: '#F8B4A8' } }}
                  cornerRadius={4}
                />
              </VictoryChart>
            </View>

            {/* List */}
            <SectionDivider label="Related Ingredients" />
            <View style={{ gap: 10 }}>
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
    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
      <Text style={{ fontSize: 12, fontWeight: '700', color: '#aaa', marginRight: 8, letterSpacing: 1 }}>
        {label.toUpperCase()}
      </Text>
      <View style={{ flex: 1, height: 1, backgroundColor: '#E5E5E5' }} />
    </View>
  );
}

function IngredientRow({ rank, item }: { rank: number; item: IngredientCorrelation }) {
  const pct = Math.round(item.triggerRate * 100);
  const barColor = pct >= 60 ? '#B8624F' : pct >= 30 ? '#F8B4A8' : '#D4E8D4';

  return (
    <View
      style={{
        backgroundColor: 'rgba(255,255,255,0.35)',
        borderRadius: 12,
        padding: 16,
        gap: 8,
      }}
    >
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
        <Text style={{ fontSize: 14, fontWeight: '700', color: '#b2939b', width: 24, textAlign: 'center' }}>
          {rank}
        </Text>
        <Text style={{ fontSize: 15, color: '#444', fontWeight: '600', flex: 1 }}>{item.name}</Text>
        <Text style={{ fontSize: 14, fontWeight: '700', color: '#7B3B4E' }}>{pct}%</Text>
      </View>

      {/* Trigger rate bar */}
      <View style={{ height: 6, backgroundColor: '#eee', borderRadius: 3, marginLeft: 36 }}>
        <View
          style={{
            height: 6,
            width: `${Math.min(pct, 100)}%`,
            backgroundColor: barColor,
            borderRadius: 3,
          }}
        />
      </View>
    </View>
  );
}
