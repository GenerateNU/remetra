import { View, StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export function LandingScreen() {
  return (
    <LinearGradient
      colors={['#F8B4A8', '#F5C76B']}
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
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 32,
    fontFamily: 'serif',
    color: '#8B4A4A',
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
    color: '#8B4A4A',
  },
  tagline: {
    fontSize: 16,
    fontFamily: 'serif',
    color: '#8B4A4A',
  },
});