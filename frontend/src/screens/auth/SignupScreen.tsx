import { View, Text, Pressable, TextInput } from 'react-native';
import { useState } from 'react';
import { useFonts } from 'expo-font';
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { authService, AuthError } from '../../api/auth_service';


export function SignupScreen() {
    const navigation = useAppNavigation();
    // start value is nothing, username is updated by setUsername(name)
    const[username, setUsername] = useState('')
    const[password, setPassword] = useState('')
    const [email, setEmail] = useState('');

    // holds error messages for each field
    const[errors, setErrors] = useState<{ username?: string; email?: string; password?: string; general?: string }>({});
    const [loading, setLoading] = useState(false);

    const [fontsLoaded] = useFonts({
      PTSerif_400Regular,
    });
  
    if (!fontsLoaded) return null;
  
    // checks if inputd are valid before calling API 
    const validate = (): boolean => {
      const newErrors: typeof errors = {};
      if (!username.trim()) newErrors.username = 'Username is required';
      if (!email.trim()) {newErrors.email = 'Email is required';} 
      else if (!/\S+@\S+\.\S+/.test(email)) {newErrors.email = 'Enter a valid email';}

      if (!password) newErrors.password = 'Password is required';
      else if (password.length < 6) newErrors.password = 'Password must be at least 6 characters';
      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    };
  
    // calls when user presses signup
    const handleSignup = async() => {

      // validate inputs (try: waits for api to respond, if it fails -> it catches error)
      if (!validate()) return;
      setLoading(true); 
      try {
        await authService.register({username, email, password});
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
            placeholderTextColor="#E5E5E5"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            className="border-b border-white text-white py-3 mb-1"
          />
          {/* if username field is error, then box turns red*/}

          {errors.username && (
            <Text className="text-red-400 mb-2">{errors.username}</Text>
          )}

          {/* email field */}

          <TextInput
            placeholder="Email"
            placeholderTextColor="#E5E5E5"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            className="border-b border-white text-white py-3 mb-6"
          />
          {/* if username field is error, then box turns red*/}
          {errors.email && (
            <Text className="text-red-400 mb-2">{errors.email}</Text>
          )}

          {/* password field */}

          <TextInput
          placeholder="Password"
          placeholderTextColor="#E5E5E5"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          autoCapitalize="none"
          className="border-b border-white text-white py-3 mb-1"
        />
        {errors.password && (
          <Text className="text-red-400 mb-2">{errors.password}</Text>
        )}

          </View>
          
          {/* buttons */}
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