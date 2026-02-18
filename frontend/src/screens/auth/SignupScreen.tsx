import { View, Text, Pressable, TextInput } from 'react-native';
import { useFonts } from 'expo-font';
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { authService, AuthError } from '../../api/auth_service';


export function SignupScreen() {
    const navigation = useAppNavigation();
  
    const [fontsLoaded] = useFonts({
      PTSerif_400Regular,
    });
  
    if (!fontsLoaded) return null;
  
    const handleSignup = () => {
      navigation.navigate('UserGoals');
    };
  
    return (
      <View className="flex-1">
        <BackgroundGradient />
  
        <View className="flex-1 justify-start items-center px-6 pt-[15%]">
        
          <View className="pt-36 items-center mb-16">
            <Text className="text-4xl text-[#F8B4A8] tracking-[7px] mb-3 font-ptserif">
              R E M E T R A
            </Text>
  
            <View className="flex-row items-center">
              <Text className="text-lg text-[#F8B4A8] italic">
                create your account{' '}
              </Text>
              <Text className="text-lg text-[#F8B4A8] font-ptserif">
                today
              </Text>
            </View>
          </View>
  
          <View className="w-full px-4">
            <TextInput
              placeholder="Username"
              placeholderTextColor="#E5E5E5"
              className="border-b border-white text-white py-3 mb-6"
            />
  
            <TextInput
              placeholder="Password"
              placeholderTextColor="#E5E5E5"
              secureTextEntry
              className="border-b border-white text-white py-3 mb-6"
            />
          </View>
  
          <View className="w-full items-center mt-10">
            <Pressable
              onPress={handleSignup}
              className="border-2 border-white rounded-none py-2.5 px-[60px] mb-4"
            >
              <Text className="text-white text-2xl font-medium">
                Sign Up
              </Text>
            </Pressable>
  
            <Pressable onPress={() => navigation.goBack()}>
              <Text className="text-white text-lg underline">
                Back
              </Text>
            </Pressable>
          </View>
        </View>
      </View>
    );
  }