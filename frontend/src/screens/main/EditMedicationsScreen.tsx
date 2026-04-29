import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { Chips } from '../../components/GenericChipComponent';
import { authService } from '../../api/auth_service';
import { useAuthStore } from '../../store/useAuthStore';

export function EditMedicationsScreen() {
  const navigation = useNavigation();
  const { user, setUserFromMe } = useAuthStore();

  const [medication, setMedication] = useState<string[]>(user.medication ?? []);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const me = await authService.updateProfile({ medication });
      setUserFromMe(me);
      navigation.goBack();
    } catch {
      Alert.alert('Error', 'Failed to update medications. Please try again.');
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
            <View className='flex-row items-center justify-between'>
              <Text className="text-xs font-semibold text-remetra-espresso/80 tracking-[1px] mb-1.5">
                MEDICATIONS
              </Text>
              <Text className="text-xs font-semibold text-remetra-muted tracking-[1px] mb-1.5">
                Press enter to add
              </Text>
            </View>
            <Chips
              items={medication}
              itemName="condition"
              placeholder="Add condition..."
              chipClassName='bg-remetra-burgundy opacity-90'
              chipTextClassName='font-semibold text-remetra-surface-accent'
              removeIconColor='#fff5f0'
              onAdd={(item) => setMedication((prev) => [...prev, item])}
              onRemove={(i) =>
                setMedication((prev) => prev.filter((_, idx) => idx !== i))
              }
            />
          </View>

          <TouchableOpacity
            onPress={handleSave}
            disabled={saving}
            className="bg-remetra-burgundy opacity-90 rounded-xl py-3 items-center"
          >
            <Text className="text-white font-semibold">
              {saving ? 'Saving...' : 'Save'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}
