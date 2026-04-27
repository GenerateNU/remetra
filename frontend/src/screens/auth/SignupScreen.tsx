import { View, Text, Pressable, TextInput, TouchableWithoutFeedback, Keyboard } from 'react-native';
import { useFonts } from 'expo-font';
import { useState } from 'react'
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { ApiError } from '../../api/client';
import { useAuthStore } from '../../store/useAuthStore';


export function SignupScreen() {
    const navigation = useAppNavigation();
    const { register } = useAuthStore()

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

    const validate = (): boolean => {
      const newErrors: typeof errors = {};

      if (!username.trim()) {
        newErrors.username = 'Username is required';
      } else if (username.trim().length < 3) {
        newErrors.username = 'Username must be at least 3 characters';
      } else if (!/^[a-zA-Z0-9_]+$/.test(username.trim())) {
        newErrors.username = 'Username can only contain letters, numbers, and underscores';
      }

      if (!email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
        newErrors.email = 'Please enter a valid email address';
      }

      if (!password) {
        newErrors.password = 'Password is required';
      } else if (password.length < 6) {
        newErrors.password = 'Password must be at least 6 characters';
      }

      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    };
  
    // calls when user presses signup
    const handleSignup = async() => {

      // validate inputs (try: waits for api to respond, if it fails -> it catches error)
      if (!validate()) return;
      setLoading(true); 
      try {
        await register({username, email, password});
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.message.includes('already registered')) { 
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
  if (!fontsLoaded) return null;
    return (
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
      <View className="flex-1">
        <BackgroundGradient />

        <View className="flex-1 justify-start items-center px-6 pt-[15%]">
        
          <View className="pt-36 items-center mb-16">
            <Text className="text-4xl text-remetra-peach tracking-[7px] mb-3 font-ptserif">
              R E M E T R A
            </Text>
  
            <View className="flex-row items-center">
              <Text className="text-lg text-remetra-peach italic">
                create your account today
              </Text>
            </View>
          </View>
  
          <View className="w-full px-4">

          {/* username field */}

          <TextInput
            placeholder="Username"
            placeholderTextColor='#B8624F' /* remetra-burgundy */
            value={username}
            onChangeText={(text) => {
              setUsername(text);
              if (errors.username) setErrors(prev => ({ ...prev, username: undefined }));
            }}
            autoCapitalize="none"
            className="border border-remetra-burgundy text-remetra-burgundy py-3 pl-2 mb-2"
          />
          {/* if username field is error, then box turns red*/}

          {errors.username && (
            <Text className="text-red-400 mb-2">{errors.username}</Text>
          )}

          {/* email field */}

          <TextInput
            placeholder="Email"
            placeholderTextColor='#B8624F' /* remetra-burgundy */
            value={email}
            onChangeText={(text) => {
              setEmail(text);
              if (errors.email) setErrors(prev => ({ ...prev, email: undefined }));
            }}
            keyboardType="email-address"
            autoCapitalize="none"
            className="border border-remetra-burgundy text-remetra-burgundy py-3 pl-2 mb-2"
          />
          {/* if username field is error, then box turns red*/}
          {errors.email && (
            <Text className="text-red-400 mb-2">{errors.email}</Text>
          )}

          {/* password field */}

          <TextInput
            placeholder="Password"
            placeholderTextColor='#B8624F' /* remetra-burgundy */
            secureTextEntry
            value={password}
            onChangeText={(text) => {
              setPassword(text);
              if (errors.password) setErrors(prev => ({ ...prev, password: undefined }));
            }}
            autoCapitalize="none"
            className="border border-remetra-burgundy text-remetra-burgundy py-3 pl-2 mb-2"
          />
          {errors.password && (
            <Text className="text-red-400 mb-2">{errors.password}</Text>
          )}
          </View>
  
          <View className="w-full items-center mt-10">
            <Pressable
              onPress={handleSignup}
              disabled={loading}
              className={`border-2 border-white rounded-none py-2.5 px-[60px] mb-4 ${loading ? 'opacity-50' : ''}`}
            >
              <Text className="text-white text-2xl font-medium">
                {loading ? 'Signing up...' : 'Sign Up'}
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
      </TouchableWithoutFeedback>
    );
  }