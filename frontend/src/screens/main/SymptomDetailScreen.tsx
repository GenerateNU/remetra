import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { TriggerRateChart } from '../../components/TriggerRateChart';
import { AssociationCard, Association } from '../../components/AssociationCard';
import { algorithmService, AlgorithmAssociationResponse } from '../../api/algorithm_service';
import { useBankStore } from '../../store/bankStore';
import { useAuthStore } from '../../store/useAuthStore';
import { MainStackParamList } from '../../navigation/stacks/MainStack';

type Props = NativeStackScreenProps<MainStackParamList, 'SymptomDetail'>;

export function SymptomDetailScreen({ route, navigation }: Props) {
  const { symptomId, symptomName } = route.params;
  const { fetchFoods } = useBankStore();
  const username = useAuthStore((s) => s.user.name);
  const [associations, setAssociations] = useState<Association[]>([]);
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

        const mapped: Association[] = results
          .map((r) => ({
            food_name: foodMap.get(r.associated_food_id) ?? r.associated_food_id,
            trigger_rate: r.key_metrics.trigger_rate,
            base_rate: r.key_metrics.base_rate,
            exposures: r.key_metrics.exposures,
            average_intensity: r.key_metrics.average_intensity,
            fishers_p_value: r.key_metrics.fishers_p_value,
          }))
          .sort((a, b) => b.trigger_rate - a.trigger_rate);

        setAssociations(mapped);
      } catch (err: any) {
        setError(err.message ?? 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

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
        ) : associations.length === 0 ? (
          <Text className="text-remetra-muted text-center mt-6 text-sm">
            No correlation data yet. Log more food and symptoms to see results.
          </Text>
        ) : (
          <>
            <TriggerRateChart
              data={associations.map(a => ({ food_name: a.food_name, trigger_rate: a.trigger_rate }))}
              title="Top Food Triggers"
            />

            <SectionDivider label="Symptom–Food Breakdown" />
            <View className="gap-1">
              {associations.map(assoc => (
                <AssociationCard key={assoc.food_name} {...assoc} />
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
