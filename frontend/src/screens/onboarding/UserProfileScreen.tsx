import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useState } from 'react';
import { useAppNavigation } from '../../navigation/hooks';
import { useFonts } from 'expo-font';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { authService } from '../../api/auth_service';

const GENDER_OPTIONS = ['Female', 'Male', 'Other'];

export function UserProfileScreen() {
  const navigation = useAppNavigation();
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('');
  const [weight, setWeight] = useState('');
  const [disease, setDisease] = useState('');
  const [medication, setMedication] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const [fontsLoaded] = useFonts({ PTSerif_400Regular });
  if (!fontsLoaded) return null;

  const handleNext = async () => {
    const newErrors: Record<string, string> = {};
    if (!dob) {
      newErrors.dob = 'Required';
    } else {
      const [mm, dd, yyyy] = dob.split('/').map(Number);
      const date = new Date(yyyy, mm - 1, dd);
      const isValid =
        dob.length === 10 &&
        date.getFullYear() === yyyy &&
        date.getMonth() === mm - 1 &&
        date.getDate() === dd &&
        yyyy >= 1900 &&
        date <= new Date();
      if (!isValid) newErrors.dob = 'Enter a valid date (MM/DD/YYYY)';
    }
    if (!gender) newErrors.gender = 'Please select a gender';
    if (!weight) newErrors.weight = 'Required';
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    const [mm, dd, yyyy] = dob.split('/').map(Number);
    const isoDate = `${yyyy}-${String(mm).padStart(2, '0')}-${String(dd).padStart(2, '0')}`;

    setLoading(true);
    try {
      await authService.updateProfile({
        dob: isoDate,
        gender,
        weight: parseFloat(weight),
        disease: disease ? [disease] : undefined,
        medication: medication
          ? medication.split('\n').map((m) => m.trim()).filter(Boolean)
          : undefined,
      });
      navigation.navigate('UserGoals');
    } catch {
      Alert.alert('Error', 'Failed to save profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView
        contentContainerClassName="flex-grow px-6 pt-[60px] pb-10"
        showsVerticalScrollIndicator={false}
      >
        {/* Brand header */}
        {/* <View className="items-center mb-8">
          <Text className="text-brand font-light font-ptserif tracking-[3px] text-remetra-accent">
            R E M E T R A
          </Text>
        </View> */}

        {/* Page title */}
        <View className="items-center mb-12 pt-16">
          <Text className="text-2xl text-remetra-rose font-ptserif text-center mb-1 font-normal">
            Tell us about yourself
          </Text>
          <Text className="text-base text-remetra-rose font-ptserif text-center opacity-60">
            This helps us personalize your experience
          </Text>
        </View>

        {/* Form card */}
        <View className="rounded-2xl px-4 py-4 gap-4 mb-4">

          {/* Date of birth */}
          <View>
            <View className="flex-row items-center mb-1.5">
              <Text className="text-sm font-ptserif text-remetra-rose opacity-80">Date of birth</Text>
              <Text className="text-remetra-rose opacity-40 ml-1 text-xs">*</Text>
            </View>
            <TextInput
              className="bg-white border border-neutral-200 rounded-xl py-3 px-4 text-remetra-burgundy font-ptserif text-base"
              placeholder="MM / DD / YYYY"
              placeholderTextColor="#D9B4A8"
              value={dob}
              onChangeText={(v) => {
                const digits = v.replace(/\D/g, '');
                let formatted = digits;
                if (digits.length >= 3 && digits.length <= 4) {
                  formatted = `${digits.slice(0, 2)}/${digits.slice(2)}`;
                } else if (digits.length > 4) {
                  formatted = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4, 8)}`;
                }
                setDob(formatted);
              }}
              keyboardType="numeric"
            />
            {errors.dob ? (
              <Text className="text-red-400 text-xs mt-1 ml-1">{errors.dob}</Text>
            ) : null}
          </View>

          {/* Gender */}
          <View>
            <View className="flex-row items-center mb-1.5">
              <Text className="text-sm font-ptserif text-remetra-rose opacity-80">Gender</Text>
              <Text className="text-remetra-rose opacity-40 ml-1 text-xs">*</Text>
            </View>
            <View className="flex-row gap-2">
              {GENDER_OPTIONS.map((option) => (
                <TouchableOpacity
                  key={option}
                  className={`flex-1 rounded-xl py-3 items-center border ${
                    gender === option
                      ? 'bg-remetra-burgundy border-remetra-burgundy'
                      : 'bg-white border-neutral-200'
                  }`}
                  onPress={() => setGender(option)}
                  activeOpacity={0.7}
                >
                  <Text
                    className={`font-ptserif text-sm ${
                      gender === option ? 'text-white' : 'text-remetra-burgundy'
                    }`}
                  >
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            {errors.gender ? (
              <Text className="text-red-400 text-xs mt-1 ml-1">{errors.gender}</Text>
            ) : null}
          </View>

          {/* Weight */}
          <View>
            <View className="flex-row items-center mb-1.5">
              <Text className="text-sm font-ptserif text-remetra-rose opacity-80">Weight (lbs)</Text>
              <Text className="text-remetra-rose opacity-40 ml-1 text-xs">*</Text>
            </View>
            <TextInput
              className="bg-white border border-neutral-200 rounded-xl py-3 px-4 text-remetra-burgundy font-ptserif text-base"
              placeholder="e.g. 140"
              placeholderTextColor="#D9B4A8"
              value={weight}
              onChangeText={setWeight}
              keyboardType="numeric"
            />
            {errors.weight ? (
              <Text className="text-red-400 text-xs mt-1 ml-1">{errors.weight}</Text>
            ) : null}
          </View>

          {/* Divider between required and optional */}
          <View className="flex-row items-center gap-2">
            <View className="flex-1 h-px bg-remetra-accent" />
            <Text className="text-xs text-remetra-rose font-ptserif">optional</Text>
            <View className="flex-1 h-px bg-remetra-accent" />
          </View>

          {/* Diagnosis */}
          <View>
            <Text className="text-sm font-ptserif text-remetra-rose opacity-80 mb-1.5">Diagnosis</Text>
            <TextInput
              className="bg-white border border-neutral-200 rounded-xl py-3 px-4 text-remetra-burgundy font-ptserif text-base"
              placeholder="e.g. Crohn's, celiac, IBS..."
              placeholderTextColor="#D9B4A8"
              value={disease}
              onChangeText={setDisease}
            />
          </View>

          {/* Medications */}
          <View>
            <Text className="text-sm font-ptserif text-remetra-rose opacity-80 mb-1.5">Current medications</Text>
            <TextInput
              className="bg-white border border-neutral-200 rounded-xl py-3 px-4 text-remetra-burgundy font-ptserif text-base"
              placeholder="List any medications, one per line..."
              placeholderTextColor="#D9B4A8"
              value={medication}
              onChangeText={setMedication}
              multiline
              numberOfLines={3}
              style={{ minHeight: 88, textAlignVertical: 'top' }}
            />
          </View>

        </View>
      </ScrollView>

      {/* Sticky CTA */}
      <View className="px-6 pb-12">
        <TouchableOpacity
          className="bg-white py-4 rounded-full items-center shadow-md"
          onPress={handleNext}
          disabled={loading}
        >
          <Text className="text-remetra-rose font-ptserif text-lg font-semibold">
            {loading ? 'Saving...' : 'Next'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
