import { useState } from 'react';
import { View, Text, TouchableOpacity, Modal } from 'react-native';

export interface Association {
  ingredient_name: string;
  trigger_rate: number;
  base_rate: number;
  exposures: number;
  average_intensity: number;
  fishers_p_value: number;
  symptom_name?: string;
}

function confidenceBadge(p: number): { label: string; color: string } {
  if (p < 0.05) return { label: 'Likely trigger', color: '#4CAF50' };
  if (p < 0.1) return { label: 'Possible trigger', color: '#FF9800' };
  return { label: 'Uncertain', color: '#9E9E9E' };
}

export function AssociationCard({
  ingredient_name,
  trigger_rate,
  base_rate,
  exposures,
  average_intensity,
  fishers_p_value,
  symptom_name,
}: Association) {
  const [expanded, setExpanded] = useState(false);
  const badge = confidenceBadge(fishers_p_value);
  const triggerPct = Math.round(trigger_rate * 100);
  const basePct = Math.round(base_rate * 100);
  const excessPct = triggerPct - basePct;

  return (
    <TouchableOpacity
      activeOpacity={0.7}
      onPress={() => setExpanded(!expanded)}
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
      {/* Collapsed: always visible */}
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Text style={{ fontSize: 15, fontWeight: '600', flex: 1 }}>{ingredient_name}</Text>
        {excessPct > 0 && (
          <Text style={{ fontSize: 14, fontWeight: '700', color: '#ca5e5e', marginRight: 12 }}>
            +{excessPct}%
          </Text>
        )}
        <Text style={{ fontSize: 12, color: '#888', marginRight: 8 }}>
          {exposures}x eaten
        </Text>
        <Text style={{ fontSize: 12, color: '#aaa' }}>{expanded ? '▾' : '▸'}</Text>
      </View>

      {/* Expanded: detail */}
      {expanded && (
        <View style={{ marginTop: 12 }}>
          {/* Confidence + symptom */}
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8, gap: 6 }}>
            <Text style={{ fontSize: 11, color: '#666' }}>Confidence:</Text>
            <View style={{ backgroundColor: badge.color, borderRadius: 10, paddingHorizontal: 8, paddingVertical: 3 }}>
              <Text style={{ color: 'white', fontSize: 11, fontWeight: '600' }}>{badge.label}</Text>
            </View>
            {symptom_name && (
              <Text style={{ fontSize: 11, color: '#b2939b', fontWeight: '500' }}>{symptom_name}</Text>
            )}
          </View>

          {/* Excess risk headline */}
          {excessPct > 0 && (
            <Text style={{ fontSize: 13, fontWeight: '600', color: '#ca5e5e', marginBottom: 10 }}>
              +{excessPct}% more likely to cause {symptom_name ?? 'symptoms'}
            </Text>
          )}

          {/* Comparison bars */}
          <View style={{ marginBottom: 12, gap: 6 }}>
            <View>
              <Text style={{ fontSize: 11, color: '#555', marginBottom: 3 }}>
                With {ingredient_name}: <Text style={{ fontWeight: '600' }}>{triggerPct}%</Text> of the time
              </Text>
              <View style={{ height: 8, backgroundColor: '#f0f0f0', borderRadius: 4 }}>
                <View
                  style={{
                    height: 8,
                    width: `${Math.min(triggerPct, 100)}%`,
                    backgroundColor: '#ca5e5e',
                    borderRadius: 4,
                  }}
                />
              </View>
            </View>
            <View>
              <Text style={{ fontSize: 11, color: '#555', marginBottom: 3 }}>
                Without: <Text style={{ fontWeight: '600' }}>{basePct}%</Text> of the time
              </Text>
              <View style={{ height: 8, backgroundColor: '#f0f0f0', borderRadius: 4 }}>
                <View
                  style={{
                    height: 8,
                    width: `${Math.min(basePct, 100)}%`,
                    backgroundColor: '#b2939b',
                    borderRadius: 4,
                  }}
                />
              </View>
            </View>
          </View>

          {/* Stats */}
          <View style={{ flexDirection: 'row', gap: 20 }}>
            <Text style={{ fontSize: 12, color: '#444' }}>
              Avg severity{' '}
              <Text style={{ fontWeight: '600' }}>{average_intensity.toFixed(1)}</Text>/10
            </Text>
          </View>
        </View>
      )}
    </TouchableOpacity>
  );
}

export function AssociationHelpButton() {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <TouchableOpacity
        onPress={() => setVisible(true)}
        style={{
          width: 28,
          height: 28,
          borderRadius: 14,
          backgroundColor: '#f0f0f0',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Text style={{ fontSize: 15, fontWeight: '700', color: '#b2939b' }}>?</Text>
      </TouchableOpacity>

      <Modal visible={visible} transparent animationType="fade">
        <TouchableOpacity
          activeOpacity={1}
          onPress={() => setVisible(false)}
          style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', padding: 24 }}
        >
          <View style={{ backgroundColor: 'white', borderRadius: 20, padding: 24 }}>
            <Text style={{ fontSize: 17, fontWeight: '700', color: '#333', marginBottom: 12 }}>
              How to read these cards
            </Text>

            <Text style={{ fontSize: 13, color: '#555', lineHeight: 20, marginBottom: 10 }}>
              Each card represents an ingredient from your food logs. Tap a card to expand it.
            </Text>

            <Text style={{ fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 4 }}>+ %</Text>
            <Text style={{ fontSize: 13, color: '#555', lineHeight: 20, marginBottom: 10 }}>
              How much more likely your symptom is after eating this ingredient. Higher = stronger link.
            </Text>

            <Text style={{ fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 4 }}>Confidence</Text>
            <Text style={{ fontSize: 13, color: '#555', lineHeight: 20, marginBottom: 4 }}>
              How statistically certain the link is:
            </Text>
            <View style={{ gap: 4, marginBottom: 10, paddingLeft: 8 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#4CAF50' }} />
                <Text style={{ fontSize: 12, color: '#555' }}>Likely trigger — strong evidence</Text>
              </View>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#FF9800' }} />
                <Text style={{ fontSize: 12, color: '#555' }}>Possible trigger — some evidence</Text>
              </View>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#9E9E9E' }} />
                <Text style={{ fontSize: 12, color: '#555' }}>Uncertain — not enough evidence yet</Text>
              </View>
            </View>

            <Text style={{ fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 4 }}>Comparison bars</Text>
            <Text style={{ fontSize: 13, color: '#555', lineHeight: 20, marginBottom: 14 }}>
              Shows how often the symptom occurs when you eat the ingredient vs. when you don't. A bigger gap means a stronger connection.
            </Text>

            <TouchableOpacity onPress={() => setVisible(false)} style={{ alignSelf: 'center', paddingVertical: 8, paddingHorizontal: 24 }}>
              <Text style={{ fontSize: 15, fontWeight: '600', color: '#b2939b' }}>Got it</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>
    </>
  );
}
