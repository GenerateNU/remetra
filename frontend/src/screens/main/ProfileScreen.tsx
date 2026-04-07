import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useAuthStore } from '../../store/useAuthStore';
import type { MainStackParamList } from '../../navigation/stacks/MainStack';

export function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();

  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>
        {/* Header */}
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
          YOUR PROFILE
        </Text>

        {/* Avatar placeholder */}
        <View style={{ alignItems: 'center', marginBottom: 24 }}>
          <View
            style={{
              width: 80,
              height: 80,
              borderRadius: 40,
              backgroundColor: '#F8B4A8',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Text style={{ fontSize: 36 }}>👤</Text>
          </View>
          {user?.name ? (
            <Text style={{ fontSize: 18, fontWeight: '600', color: '#7B3B4E', marginTop: 12 }}>
              {user.name}
            </Text>
          ) : null}
          {user?.email ? (
            <Text style={{ fontSize: 14, color: '#aaa', marginTop: 4 }}>{user.email}</Text>
          ) : null}
        </View>

        {/* Actions */}
        <View style={{ gap: 12 }}>
          <SectionDivider label="Account" />

          <ActionRow
            emoji="📋"
            label="Manage Symptom & Food Bank"
            onPress={() => {}}
          />

          <SectionDivider label="App" />

          <ActionRow
            emoji="ℹ️"
            label="About Remetra"
            onPress={() => {}}
          />

          <SectionDivider label="Session" />

          <TouchableOpacity
            onPress={() => useAuthStore.setState({ hasCompletedOnboarding: false })}
            style={{
              backgroundColor: '#FEF0E7',
              borderRadius: 12,
              padding: 16,
              flexDirection: 'row',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <Text style={{ fontSize: 20 }}>↩️</Text>
            <Text style={{ fontSize: 15, color: '#A0673A', flex: 1 }}>Reset Onboarding</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={logout}
            style={{
              backgroundColor: '#B8624F',
              borderRadius: 12,
              padding: 16,
              alignItems: 'center',
              marginTop: 8,
            }}
          >
            <Text style={{ color: 'white', fontSize: 16, fontWeight: '600' }}>Log Out</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 8, marginBottom: 4 }}>
      <Text style={{ fontSize: 12, fontWeight: '700', color: '#aaa', marginRight: 8, letterSpacing: 1 }}>
        {label.toUpperCase()}
      </Text>
      <View style={{ flex: 1, height: 1, backgroundColor: '#E5E5E5' }} />
    </View>
  );
}

function ActionRow({
  emoji,
  label,
  onPress,
}: {
  emoji: string;
  label: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={{
        backgroundColor: 'rgba(255,255,255,0.7)',
        borderRadius: 12,
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
      }}
    >
      <Text style={{ fontSize: 20 }}>{emoji}</Text>
      <Text style={{ fontSize: 15, color: '#444', flex: 1 }}>{label}</Text>
      <Text style={{ fontSize: 18, color: '#ccc' }}>›</Text>
    </TouchableOpacity>
  );
}
