import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, TextInput } from 'react-native';
import { ArrowLeft } from 'lucide-react-native';
import { useEffect, useMemo } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { AssociationCard, AssociationHelpButton } from '../../components/AssociationCard';
import { useAlgorithmStore, EnrichedAssociation } from '../../store/useAlgorithmStore';
import { useAuthStore } from '../../store/useAuthStore';
import { MainStackParamList } from '../../navigation/stacks/MainStack';

type Props = NativeStackScreenProps<MainStackParamList, 'Correlations'>;

export function CorrelationsScreen({ navigation, route }: Props) {
  const userId = useAuthStore.getState().user.name ?? 'user_001';
  const { associationsBySymptom, symptoms, isLoading, error, fetchAssociations, minExposures, setMinExposures } = useAlgorithmStore();

  useEffect(() => {
    if (userId) fetchAssociations(userId);
  }, [userId]);
  const selectedSymptomId = route.params?.initialSymptomId ?? null;

  const hasData = symptoms.length > 0;

  const filteredBySymptom = useMemo(() => {
    const result: Record<string, EnrichedAssociation[]> = {};
    for (const [symptomId, assocs] of Object.entries(associationsBySymptom)) {
      const filtered = assocs.filter(a => a.exposures >= minExposures);
      if (filtered.length > 0) result[symptomId] = filtered;
    }
    return result;
  }, [associationsBySymptom, minExposures]);

  const filteredSymptoms = symptoms.filter(s => filteredBySymptom[s.id]);

  const activeSymptomId = selectedSymptomId ?? filteredSymptoms[0]?.id ?? null;
  const activeAssociations = activeSymptomId
    ? (filteredBySymptom[activeSymptomId] ?? []).slice().sort((a, b) => b.trigger_rate - a.trigger_rate)
    : [];
  const activeName = symptoms.find(s => s.id === activeSymptomId)?.name ?? '';

  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <View style={{ flex: 1 }}>
        {/* Header */}
        <View style={{ paddingTop: 56, paddingHorizontal: 24, paddingBottom: 8 }}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={{ marginBottom: 8, flexDirection: 'row', alignItems: 'center', gap: 6 }}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <ArrowLeft size={16} color="#ca5e5e" strokeWidth={2} />
            <Text style={{ color: '#ca5e5e', fontSize: 14 }}>Back</Text>
          </TouchableOpacity>
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <Text style={{ fontSize: 24, fontWeight: '600', color: '#b2939b', fontStyle: 'italic', textTransform: 'capitalize' }}>
              {activeName}
            </Text>
            <AssociationHelpButton />
          </View>
        </View>

        {/* Main content */}
        <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 32 }}>
          {isLoading ? (
            <ActivityIndicator color="#b2939b" style={{ marginTop: 48 }} />
          ) : error ? (
            <Text style={{ textAlign: 'center', color: '#ca5e5e', marginTop: 40 }}>{error}</Text>
          ) : !hasData ? (
            <Text style={{ textAlign: 'center', color: '#888', marginTop: 40 }}>
              No correlation data yet. Log more food and symptoms to see results.
            </Text>
          ) : (
            <>
              {/* Min exposures filter */}
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 16, gap: 8 }}>
                <Text style={{ fontSize: 13, color: '#888' }}>Min exposures:</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                  <TouchableOpacity
                    onPress={() => setMinExposures(minExposures - 1)}
                    style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <Text style={{ fontSize: 18, fontWeight: '600', color: '#666' }}>-</Text>
                  </TouchableOpacity>
                  <TextInput
                    value={String(minExposures)}
                    onChangeText={text => {
                      const n = parseInt(text, 10);
                      if (!isNaN(n) && n >= 1) setMinExposures(n);
                    }}
                    keyboardType="number-pad"
                    style={{
                      width: 48,
                      height: 32,
                      textAlign: 'center',
                      fontSize: 15,
                      fontWeight: '600',
                      color: '#333',
                      backgroundColor: 'white',
                      borderRadius: 8,
                      borderWidth: 1,
                      borderColor: '#ddd',
                    }}
                  />
                  {filteredSymptoms.length === 0 ?(
                    <></>
                  ) : (
                    <TouchableOpacity
                      onPress={() => setMinExposures(minExposures + 1)}
                      style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0', alignItems: 'center', justifyContent: 'center' }}
                    >
                      <Text style={{ fontSize: 18, fontWeight: '600', color: '#666' }}>+</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>

              {filteredSymptoms.length === 0 ? (
                <Text style={{ textAlign: 'center', color: '#888', marginTop: 20 }}>
                  No correlations with {minExposures}+ exposures. Try lowering the minimum.
                </Text>
              ) : (
              <>
              {/* Per-symptom ingredients */}
              {activeAssociations.length > 0 && (
                <View style={{ marginBottom: 32 }}>
                  {activeAssociations.map(assoc => (
                    <AssociationCard key={assoc.ingredient_name} {...assoc} />
                  ))}
                </View>
              )}
              </>
              )}
            </>
          )}
        </ScrollView>
      </View>
    </View>
  );
}
