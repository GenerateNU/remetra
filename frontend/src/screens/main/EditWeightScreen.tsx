import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { authService } from '../../api/auth_service';
import { useAuthStore } from '../../store/useAuthStore';

export function EditWeightScreen() {
  const navigation = useNavigation();
  const { user, setUserFromMe } = useAuthStore();

  const [weight, setWeight] = useState<string>(
    user.weight != null ? String(user.weight) : ''
  );
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!weight) {
      setError('Required');
      return;
    }
    const parsed = parseFloat(weight);
    if (Number.isNaN(parsed)) {
      setError('Enter a valid number');
      return;
    }
    setError(null);
    setSaving(true);
    try {
      const me = await authService.updateProfile({ weight: parsed });
      setUserFromMe(me);
      navigation.goBack();
    } catch {
      Alert.alert('Error', 'Failed to update weight. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24 }}>
        <View className="bg-white/70 rounded-xl p-4 gap-4">
          <View>
            <Text className="text-xs font-bold text-neutral-500 tracking-[1px] mb-1.5">
              WEIGHT (LBS)
            </Text>
            <TextInput
              className="bg-white border border-neutral-200 rounded-xl py-3 px-4 text-neutral-600"
              placeholder="e.g. 140"
              placeholderTextColor="#676767"
              value={weight}
              onChangeText={setWeight}
              keyboardType="numeric"
              autoFocus
            />
            {error ? (
              <Text className="text-red-400 text-xs mt-1 ml-1">{error}</Text>
            ) : null}
          </View>

          <TouchableOpacity
            onPress={handleSave}
            disabled={saving}
            className="bg-remetra-burgundy rounded-xl py-3 items-center"
          >
            <Text className="text-white font-bold">
              {saving ? 'Saving...' : 'Save'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}
