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
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>
        <Text className="text-2xl font-semibold text-remetra-mauve italic tracking-[1px] text-center mb-8">
          YOUR PROFILE
        </Text>

        {/* Avatar */}
        <View className="items-center mb-6">
          <View className="w-20 h-20 rounded-full bg-remetra-peach justify-center items-center">
            <Text className="text-4xl">👤</Text>
          </View>
          {user?.name ? (
            <Text className="text-lg font-semibold text-remetra-rose mt-3">{user.name}</Text>
          ) : null}
          {user?.email ? (
            <Text className="text-sm text-remetra-muted mt-1">{user.email}</Text>
          ) : null}
        </View>

        {/* Actions */}
        <View className="gap-3">
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
            onPress={() => navigation.navigate('About')}
          />

          <SectionDivider label="Session" />

          <TouchableOpacity
            onPress={() => useAuthStore.setState({ hasCompletedOnboarding: false })}
            className="bg-remetra-surface-accent rounded-xl p-4 flex-row items-center gap-3"
          >
            <Text className="text-xl">↩️</Text>
            <Text className="text-[15px] text-remetra-burgundy flex-1">Reset Onboarding</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={logout}
            className="bg-remetra-burgundy rounded-xl p-4 items-center mt-2"
          >
            <Text className="text-white text-base font-semibold">Log Out</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View className="flex-row items-center mt-2 mb-1">
      <Text className="text-xs font-bold text-remetra-muted mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-neutral-200" />
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
      className="bg-white/70 rounded-xl p-4 flex-row items-center gap-3"
    >
      <Text className="text-xl">{emoji}</Text>
      <Text className="text-[15px] text-neutral-700 flex-1">{label}</Text>
      <Text className="text-lg text-remetra-border">›</Text>
    </TouchableOpacity>
  );
}
