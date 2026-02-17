import { View, Text, Pressable } from 'react-native';
import { useFonts } from 'expo-font';
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';

export function SignupScreen() {
    const navigation = useAppNavigation();
  
    const [fontsLoaded] = useFonts({
      PTSerif_400Regular,
    });
  
    if (!fontsLoaded) return null;
  
    const handleSignup = () => {
      navigation.navigate('UserGoals');
    };
  
    // calls when user presses signup
    const handleSignup = async() => {

      // validate inputs (try: waits for api to respond, if it fails -> it catches error)
      if (!validate()) return;
      setLoading(true); 
      try {
        //await authService.register({username, email, password});
        navigation.navigate('UserGoals');
    } catch (err) {
      if (err instanceof AuthError) {
        if (err.message.includes('already exists')) { 
          setErrors({ username: 'Username already taken' });
        } else {
          setErrors({ general: err.message });
        }
      } else {
        setErrors({ general: 'Something went wrong. Please try again.' }); 
      }
    } finally {
      setLoading(false); 
    }
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

          {/* username field */}

          <TextInput
            placeholder="Username"
            placeholderTextColor='#B8624F'
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            className="border-b border-white text-white py-3 pl-2 mb-2"
            style={{
              borderColor: '#B8624F',
              borderWidth: 1,
              color: '#B8624F',
            }}
          />
          {/* if username field is error, then box turns red*/}

          {errors.username && (
            <Text className="text-red-400 mb-2">{errors.username}</Text>
          )}

          {/* email field */}

          <TextInput
            placeholder="Email"
            placeholderTextColor='#B8624F'
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            className="border-b border-white text-white py-3 pl-2 mb-2"
            style={{
              borderColor: '#B8624F',
              borderWidth: 1,
              color: '#B8624F',
            }}
          />
          {/* if username field is error, then box turns red*/}
          {errors.email && (
            <Text className="text-red-400 mb-2">{errors.email}</Text>
          )}

          {/* password field */}

          <TextInput
          placeholder="Password"
          placeholderTextColor='#B8624F'
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          autoCapitalize="none"
          className="border-b border-white text-white py-3 pl-2 mb-2"
          style={{
            borderColor: '#B8624F',
            borderWidth: 1,
            color: '#B8624F',
          }}
        />
        {errors.password && (
          <Text className="text-red-400 mb-2">{errors.password}</Text>
        )}

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