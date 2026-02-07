import { View, StyleSheet, Text, Pressable } from 'react-native';
import { useAppNavigation } from '../../navigation/hooks';
import { BackgroundGradient } from '../../components/BackgroundGradient';

export function LandingScreen() {

  const navigation = useAppNavigation();
  
  return (
    <View className='flex-1'> 
      <BackgroundGradient />
        <View className='flex-1 justify-start items-center px-6 pt-[15%]'>
          <View style={styles.header} className='pt-36'> 
          <Text style={styles.title}>R E M E T R A</Text>
          <View style={styles.taglineContainer}>
            <Text style={styles.taglineItalic}>peace of mind </Text>
            <Text style={styles.tagline}>begins here</Text>
          </View>
        </View> 
    

        {/* Buttons */}
        <View style={styles.buttonContainer}>
          <Pressable 
            style={styles.loginButton}
            onPress={() => navigation.navigate("UserGoals")}
          >
            <Text style={styles.loginButtonText}>Log in</Text>
          </Pressable>

          <View style={styles.signupContainer}>
              <Text style={styles.signupText}>New user? </Text>
              <Pressable onPress={() => navigation.navigate("UserGoals")}>
                <Text style={styles.signupLink}>   Sign up</Text>
              </Pressable>
          </View>
        </View>
      </View>  
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: '15%',
  },
  title: {
    fontSize: 32,
    fontFamily: 'serif',
    color: '#F8B4A8',
    letterSpacing: 8,
    marginBottom: 12,
  },
  taglineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  taglineItalic: {
    fontSize: 16,
    fontFamily: 'serif',
    fontStyle: 'italic',
    color: '#F8B4A8',
  },
  tagline: {
    fontSize: 16,
    fontFamily: 'serif',
    color: '#F8B4A8',
  },
  buttonContainer: {
    width: '100%',
    alignItems: 'center',
    marginTop: 150,    
  },
  loginButton: {
    borderWidth: 2,
    borderColor: '#FFFFFF',
    borderRadius: 0,
    paddingVertical: 10,
    paddingHorizontal: 60,
    marginBottom: 16,
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '500',
    
  },
  signupContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  signupText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontFamily: 'serif',
  },
  signupLink: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'serif',
  },
  header: {
  alignItems: 'center',
},

});   