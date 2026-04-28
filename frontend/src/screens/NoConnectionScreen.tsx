import { View, Text } from 'react-native';
import { useFonts } from 'expo-font';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../components/BackgroundGradient';

export function NoConnectionScreen() {
  const [fontsLoaded] = useFonts({
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null;
  }

  return (
    <View className="flex-1">
      <BackgroundGradient />
      <View className="flex-1 justify-center items-center px-8">
        <Text className="text-4xl text-remetra-peach tracking-[7px] mb-6 font-ptserif">
          R E M E T R A
        </Text>
        {/* React native icon no signal */}
        <Text className="text-xl text-remetra-burgundy font-ptserif mb-4 text-center">
          Please Connect to the Internet
        </Text>
      </View>
    </View>
  );
}
