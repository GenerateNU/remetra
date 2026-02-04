import { View, StyleSheet, Text, Pressable } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppNavigation } from '../../navigation/hooks';

export function LandingScreen() {

  const navigation = useAppNavigation();
  
  return (
    <LinearGradient
      colors={['#FFFFFF', '#FFFFFF',  '#F5C76B','#F8B4A8',]}
      locations={[0, 0.5, 0.7, 1]}
      style={styles.container}
      start={{ x: 0.5, y: 0 }}
      end={{ x: 0.5, y: 1 }}
    >
      <View style={styles.content}>
        <View style={styles.header}> 
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
              <Text style={styles.signupLink}>Sign up</Text>
            </Pressable>
        </View>
       </View>
     </View>
    

    </LinearGradient>
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
    marginTop: 175,    
  },
  loginButton: {
    borderWidth: 2,
    borderColor: '#FFFFFF',
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 80,
    marginBottom: 16,
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '500',
  },
  signupContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  signupText: {
    color: '#FFFFFF',
    fontSize: 14,
  },
  signupLink: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  header: {
  alignItems: 'center',
},

});   