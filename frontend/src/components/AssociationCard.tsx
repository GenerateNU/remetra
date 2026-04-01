import { View, Text } from 'react-native';

export interface Association {
  food_name: string;
  trigger_rate: number;
  base_rate: number;
  exposures: number;
  average_intensity: number;
  fishers_p_value: number;
}

function confidenceBadge(p: number): { label: string; color: string } {
  if (p < 0.05) return { label: 'High confidence', color: '#4CAF50' };
  if (p < 0.1) return { label: 'Medium confidence', color: '#FF9800' };
  return { label: 'Low confidence', color: '#9E9E9E' };
}

export function AssociationCard({
  food_name,
  trigger_rate,
  base_rate,
  exposures,
  average_intensity,
  fishers_p_value,
}: Association) {
  const badge = confidenceBadge(fishers_p_value);
  const triggerPct = Math.min(Math.round(trigger_rate * 100), 100);
  const basePct = Math.min(Math.round(base_rate * 100), 100);

  return (
    <View
      style={{
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 16,
        marginVertical: 6,
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowRadius: 4,
        shadowOffset: { width: 0, height: 2 },
        elevation: 2,
      }}
    >
      {/* Header row */}
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <Text style={{ fontSize: 16, fontWeight: '600', flex: 1 }}>{food_name}</Text>
        <View style={{ backgroundColor: badge.color, borderRadius: 10, paddingHorizontal: 8, paddingVertical: 3 }}>
          <Text style={{ color: 'white', fontSize: 11, fontWeight: '600' }}>{badge.label}</Text>
        </View>
      </View>

      {/* Trigger rate bar */}
      <Text style={{ fontSize: 11, color: '#666', marginBottom: 4 }}>
        Trigger rate: {triggerPct}%  ·  Baseline: {basePct}%
      </Text>
      <View style={{ height: 6, backgroundColor: '#f0f0f0', borderRadius: 3, marginBottom: 12 }}>
        <View
          style={{
            height: 6,
            width: `${triggerPct}%`,
            backgroundColor: '#ca5e5e',
            borderRadius: 3,
          }}
        />
        {/* Baseline marker */}
        <View
          style={{
            position: 'absolute',
            left: `${basePct}%`,
            top: -2,
            width: 2,
            height: 10,
            backgroundColor: '#555',
            borderRadius: 1,
          }}
        />
      </View>

      {/* Stats row */}
      <View style={{ flexDirection: 'row', gap: 20 }}>
        <Text style={{ fontSize: 12, color: '#444' }}>
          <Text style={{ fontWeight: '600' }}>{exposures}</Text> exposures
        </Text>
        <Text style={{ fontSize: 12, color: '#444' }}>
          Avg intensity{' '}
          <Text style={{ fontWeight: '600' }}>{average_intensity.toFixed(1)}</Text>/10
        </Text>
      </View>
    </View>
  );
}
