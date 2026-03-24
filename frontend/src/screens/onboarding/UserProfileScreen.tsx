import { View, Text, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { useState } from 'react';
import { useAppNavigation } from '../../navigation/hooks';
import { useFonts } from 'expo-font';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';

const GENDER_OPTIONS = ['Female', 'Male', 'Other'];

export function UserProfileScreen() {
  const navigation = useAppNavigation();
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('');
  const [weight, setWeight] = useState('');
  const [disease, setDisease] = useState('');
  const [medication, setMedication] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});

  const [fontsLoaded] = useFonts({ PTSerif_400Regular });
  if (!fontsLoaded) return null;

  const handleNext = () => {
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
      if (!isValid) newErrors.dob = 'Enter a valid date';
    }
    if (!gender) newErrors.gender = 'Required';
    if (!weight) newErrors.weight = 'Required';
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;
    navigation.navigate('UserGoals');
  };

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView
        contentContainerClassName="flex-grow px-6 pt-[60px] pb-10"
        showsVerticalScrollIndicator={false}
      >
        <View className="items-center mb-10">
          <Text className="text-[32px] font-light font-ptserif tracking-[3px] text-[#eea487]">
            R E M E T R A
          </Text>
        </View>

        <View className="flex-1">
          <Text className="text-xl text-[#C85A4A] font-ptserif text-center mb-2 font-normal">
            Tell us about yourself
          </Text>
          <Text className="text-base text-[#C85A4A] font-ptserif text-center mb-8 opacity-80">
            This helps us personalize your experience
          </Text>

          <View className="gap-5 mb-10">

            {/* Date of birth */}
            <View>
              <Text className="text-[#C85A4A] font-ptserif text-lg mb-2 opacity-80">Date of birth</Text>
              <TextInput
                className="bg-[#D9806E] rounded-xl py-4 px-5 text-white font-ptserif text-lg"
                placeholder="MM / DD / YYYY"
                placeholderTextColor="rgba(255,255,255,0.6)"
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
              {errors.dob
                ? <Text className="text-red-300 text-xs mt-1 ml-1">{errors.dob}</Text>
                : <Text className="text-[#C85A4A] text-xs mt-1 ml-1 opacity-60">Required</Text>
              }
            </View>

            {/* Gender */}
            <View>
              <Text className="text-[#C85A4A] font-ptserif text-lg mb-2 opacity-80">Gender</Text>
              <View className="flex-row gap-3">
                {GENDER_OPTIONS.map((option) => (
                  <TouchableOpacity
                    key={option}
                    className="flex-1 rounded-xl py-4 items-center"
                    style={{ backgroundColor: gender === option ? '#B8624F' : '#D9806E' }}
                    onPress={() => setGender(option)}
                    activeOpacity={0.7}
                  >
                    <Text className="text-white font-ptserif text-sm">{option}</Text>
                  </TouchableOpacity>
                ))}
              </View>
              <Text className="text-[#C85A4A] text-xs mt-1 ml-1 opacity-60">Required</Text>
            </View>

            {/* Weight */}
            <View>
              <Text className="text-[#C85A4A] font-ptserif text-lg mb-2 opacity-80">Weight (lbs)</Text>
              <TextInput
                className="bg-[#D9806E] rounded-xl py-4 px-5 text-white font-ptserif text-lg"
                placeholder="Enter your weight"
                placeholderTextColor="rgba(255,255,255,0.6)"
                value={weight}
                onChangeText={setWeight}
                keyboardType="numeric"
              />
              <Text className="text-[#C85A4A] text-xs mt-1 ml-1 opacity-60">Required</Text>
            </View>

            {/* Disease */}
            <View>
              <Text className="text-[#C85A4A] font-ptserif text-lg mb-2 opacity-80">Diagnosis</Text>
              <TextInput
                className="bg-[#D9806E] rounded-xl py-4 px-5 text-white font-ptserif text-lg"
                placeholder="e.g. Crohn's, celiac..."
                placeholderTextColor="rgba(255,255,255,0.6)"
                value={disease}
                onChangeText={setDisease}
              />
              {errors.disease && <Text className="text-red-200 text-xs mt-1 ml-1">{errors.disease}</Text>}
            </View>

            {/* Medication */}
            <View>
              <Text className="text-[#C85A4A] font-ptserif text-lg mb-2 opacity-80">
                Current medications
              </Text>
              <TextInput
                className="bg-[#D9806E] rounded-xl py-4 px-5 text-white font-ptserif text-lg"
                placeholder="List any medications..."
                placeholderTextColor="rgba(255,255,255,0.6)"
                value={medication}
                onChangeText={setMedication}
                multiline
                numberOfLines={3}
              />
            </View>

          </View>
        </View>
      </ScrollView>

      <View className="px-6 pb-12">
        <TouchableOpacity
          className="bg-white py-4 rounded-[25px] items-center shadow-md"
          onPress={handleNext}
        >
          <Text className="text-[#C85A4A] font-ptserif text-lg font-semibold">
            Next
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}