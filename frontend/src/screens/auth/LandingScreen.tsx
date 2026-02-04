import { View, StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export function LandingScreen() {
  return (
    <LinearGradient
      colors={['#FFFFFF', '#FFFFFF', '#F8B4A8', '#F5C76B']}
      locations={[0, 0.5, 0.7, 1]}
      style={styles.container}
      start={{ x: 0.5, y: 0 }}
      end={{ x: 0.5, y: 1 }}
    >
      <View style={styles.content}>
        <Text style={styles.title}>R E M E T R A</Text>
        <View style={styles.taglineContainer}>
          <Text style={styles.taglineItalic}>peace of mind </Text>
          <Text style={styles.tagline}>begins here</Text>
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
    paddingTop: '30%',
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
});