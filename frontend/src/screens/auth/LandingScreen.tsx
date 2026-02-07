import { View, Text, Pressable } from 'react-native';
import { useFonts } from 'expo-font';
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';

export function LandingScreen() {
  const navigation = useAppNavigation();
  
  const [fontsLoaded] = useFonts({
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null; 
  }
  
  return (
    <View className="flex-1"> 
      <BackgroundGradient />
      <View className="flex-1 justify-start items-center px-6 pt-[15%]">
        
        {/* Title Section */}
        <View className="pt-36 items-center"> 
          <Text className="text-4xl text-[#F8B4A8] tracking-[7px] mb-3 font-ptserif">
            R E M E T R A
          </Text>
          
          <View className="flex-row items-center">
            <Text className="text-lg text-[#F8B4A8] italic">
              peace of mind{' '}
            </Text>
            <Text className="text-lg text-[#F8B4A8] font-ptserif">
              begins here
            </Text>
          </View>
        </View> 
    
        {/* Buttons */}
        <View className="w-full items-center mt-[150px]">
          <Pressable 
            className="border-2 border-white rounded-none py-2.5 px-[60px] mb-4"
            onPress={() => navigation.navigate("UserGoals")}
          >
            <Text className="text-white text-2xl font-medium">
              Log in
            </Text>
          </Pressable>

          <View className="flex-row items-center">
            <Text className="text-white text-lg">
              New user?{' '}
            </Text>
            <Pressable onPress={() => navigation.navigate("UserGoals")}>
              <Text className="text-white text-xl font-semibold">
                Sign up
              </Text>
            </Pressable>
          </View>
        </View>
      </View>  
    </View>
  );
}