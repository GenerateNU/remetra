import React from 'react';
import { View, Text } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';

export function AnalysisScreen() {
  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 }}>
        <Text
          style={{
            fontSize: 24,
            fontWeight: '600',
            color: '#b2939b',
            fontStyle: 'italic',
            letterSpacing: 1,
            textAlign: 'center',
            marginBottom: 16,
          }}
        >
          YOUR ANALYSIS
        </Text>
        <Text style={{ fontSize: 14, color: '#aaa', textAlign: 'center' }}>
          Coming soon.
        </Text>
      </View>
    </View>
  );
}
