import { View, Text, Pressable, TextInput, ActivityIndicator } from 'react-native';
import { useState } from 'react';
import { useFonts } from 'expo-font';
import { useAppNavigation } from '../../navigation/hooks';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { authService, AuthError } from '../../api/auth_service';

export function LoginScreen() {
  const navigation = useAppNavigation();

  const[username, setUsername] = useState('')
  const[password, setPassword] = useState('')
  // holds error messages for each field
  const[errors, setErrors] = useState<{ username?: string; password?: string; general?: string }>({});
  const [loading, setLoading] = useState(false);


  const [fontsLoaded] = useFonts({
    PTSerif_400Regular,
  });

  if (!fontsLoaded) return null;

  // checks if inputd are valid before calling API 
  const validate = (): boolean => {
    const newErrors: typeof errors = {}
    if (!username.trim()) newErrors.username = 'Username is required';
    if (!password) newErrors.password = 'Password is required';
    else if (password.length < 6) newErrors.password = 'Password must be at least 6 characters';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // calls when user presses login
  const handleLogin = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      //await authService.login({ username, password });
      navigation.navigate('UserGoals');
    } catch (err) {
      if (err instanceof AuthError) {
        if (err.message.includes('Incorrect')) setErrors({ password: 'Incorrect username or password' });
        else setErrors({ general: err.message });
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
              welcome{' '}
            </Text>
            <Text className="text-lg text-[#F8B4A8] font-ptserif">
              back
            </Text>
          </View>
        </View>

        {/* username field — turns red border if there's an error */}

        <View className="w-full px-4">
          <TextInput
            placeholder="Username"
            placeholderTextColor="#B8624F"
            autoCapitalize="none"
            value={username}
            onChangeText={setUsername}
            className={`border-b py-3 mb-2 pl-2 text-white ${errors.username ? 'border-red-400' : 'border-white'}`}
            // Manually insert custom colors with style (we should update this to use nativewind in future)
            style={{
              borderColor: '#B8624F',
              borderWidth: 1,
              color: '#B8624F',
            }}
          />
         {/* show username error if it exists */}
          {errors.username && <Text className="text-red-400 text-sm mb-4">{errors.username}</Text>}

         {/* password field — turns red border if there's an error */}
          <TextInput
            placeholder="Password"
            placeholderTextColor="#B8624F"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
            // condition: if there's a error for password, its red, if none, white 
            className={`border-b py-3 mb-2 pl-2 text-white ${errors.password ? 'border-red-400' : 'border-white'}`}
            // Manually insert custom colors with style (we should update this to use nativewind in future)
            style={{
              borderColor: '#B8624F',
              borderWidth: 1,
              color: '#B8624F',
            }}
          />
          {errors.password && <Text className="text-red-400 text-sm mb-4">{errors.password}</Text>}
          {errors.general && <Text className="text-red-400 text-sm mb-4">{errors.general}</Text>}
        </View>

        {/* buttons */}
        <View className="w-full items-center mt-10">
          <Pressable
            onPress={handleLogin}disabled={loading}
            className="border-2 border-white rounded-none py-2.5 px-[60px] mb-4"
          >
             {/* show spinner while waiting for API, otherwise show button text */}
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="text-white text-2xl font-medium">
                Log In
              </Text>
            )}
          </Pressable>

        {/* Back button — goes back to Landing screen */}

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