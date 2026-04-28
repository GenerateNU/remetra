import React, { useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useAuthStore } from '../../store/useAuthStore';
import type { MainStackParamList } from '../../navigation/stacks/MainStack';

export function ProfileScreen() {
  const { user, logout, refreshProfile } = useAuthStore();
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();

  useFocusEffect(
    useCallback(() => {
      refreshProfile().catch(() => {
        // Silent — fall back to whatever is in the persisted store.
      });
    }, [refreshProfile])
  );

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>
        {/* Avatar */}
        <View className="items-center mb-6">
          <View className="w-20 h-20 rounded-full bg-remetra-peach justify-center items-center">
            <Text className="text-4xl">🌺</Text>
          </View>
          {user?.name ? (
            <Text className="text-lg font-semibold text-remetra-rose mt-3">{user.name}</Text>
          ) : null}
          {user?.email ? (
            <Text className="text-sm text-remetra-muted mt-1">{user.email}</Text>
          ) : null}
        </View>

        <View className="gap-3">
          <SectionDivider label="Health Profile" />

          <View className="bg-white/70 rounded-xl overflow-hidden">
            <ReadOnlyRow
              label="Date of Birth"
              value={formatDobForDisplay(user.dob) || '—'}
            />
            <RowSeparator />
            <ReadOnlyRow label="Gender" value={user.gender ?? '—'} />
            <RowSeparator />
            <EditableRow
              label="Weight"
              value={user.weight != null ? `${user.weight} lbs` : '—'}
              onPress={() => navigation.navigate('EditWeight')}
            />
            <RowSeparator />
            <EditableChipRow
              label="Conditions"
              items={user.disease}
              onPress={() => navigation.navigate('EditConditions')}
            />
            <RowSeparator />
            <EditableChipRow
              label="Medications"
              items={user.medication}
              onPress={() => navigation.navigate('EditMedications')}
            />
          </View>

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
      <Text className="text-xs font-bold text-neutral-500 mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-neutral-100" />
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

function ReadOnlyRow({ label, value }: { label: string; value: string }) {
  return (
    <View className="flex-row justify-between items-center px-4 py-3.5">
      <Text className="text-xs font-bold text-neutral-500 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <Text className="text-[15px] text-neutral-700">{value}</Text>
    </View>
  );
}

function EditableRow({
  label,
  value,
  onPress,
}: {
  label: string;
  value: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity
      onPress={onPress}
      className="flex-row justify-between items-center px-4 py-3.5"
    >
      <Text className="text-xs font-bold text-neutral-500 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-row items-center gap-2">
        <Text className="text-[15px] text-neutral-700">{value}</Text>
        <Text className="text-lg text-remetra-border">›</Text>
      </View>
    </TouchableOpacity>
  );
}

function EditableChipRow({
  label,
  items,
  onPress,
}: {
  label: string;
  items: string[];
  onPress: () => void;
}) {
  return (
    <TouchableOpacity onPress={onPress} className="px-4 py-3.5">
      <View className="flex-row justify-between items-center mb-1.5">
        <Text className="text-xs font-bold text-neutral-500 tracking-[1px]">
          {label.toUpperCase()}
        </Text>
        <Text className="text-lg text-remetra-border">›</Text>
      </View>
      {items.length === 0 ? (
        <Text className="text-[15px] text-neutral-400">—</Text>
      ) : (
        <View className="flex-row flex-wrap gap-2">
          {items.map((item, i) => (
            <View
              key={`${item}-${i}`}
              className="bg-remetra-burgundy opacity-80 rounded-full py-1.5 px-3"
            >
              <Text className="text-sm font-semibold text-remetra-surface-accent">{item}</Text>
            </View>
          ))}
        </View>
      )}
    </TouchableOpacity>
  );
}

function RowSeparator() {
  return <View className="h-px bg-white mx-6" />;
}

function formatDobForDisplay(iso: string | null): string {
  if (!iso) return '';
  const [yyyy, mm, dd] = iso.split('-');
  if (!yyyy || !mm || !dd) return '';
  return `${mm}/${dd}/${yyyy}`;
}
