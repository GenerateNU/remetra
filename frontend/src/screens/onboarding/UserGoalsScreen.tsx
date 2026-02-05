import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import Svg, { Defs, RadialGradient, Stop, Rect } from 'react-native-svg';
import { useState } from 'react';
// import { useAppNavigation } from '../../navigation/hooks';
import { useFonts } from 'expo-font';
import { Lora_400Regular } from '@expo-google-fonts/lora';
import { PTSerif_400Regular } from '@expo-google-fonts/pt-serif';


const GOAL_OPTIONS = [
  'Track symptoms related to autoimmune disease',
  'Identify trigger ingredients',
  'Discover correlations between current habits',
  'Improve quality of life through informed changes',
];

export function UserGoalsScreen() {
  // const navigation = useAppNavigation();
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const [fontsLoaded] = useFonts({
    Lora_400Regular,
    PTSerif_400Regular,
  });

  if (!fontsLoaded) {
    return null; 
  }

  const toggleGoal = (goal: string) => {
    if (selectedGoals.includes(goal)) {
      setSelectedGoals(selectedGoals.filter(g => g !== goal));
    } else {
      setSelectedGoals([...selectedGoals, goal]);
    }
  };

  // navigate to the final onboarding screen here, replace name? 
  const handleDone = () => {
    // navigation.navigate('finalboardingscreen?'); 
    // TODO: navigate to onboarding screen when implemented
  };

  return (
    <View style={styles.container}>
      <Svg height="100%" width="100%" style={StyleSheet.absoluteFill}>
        <Defs>
          <RadialGradient id="grad" cx="50%" cy="95%" r="60%">
            <Stop offset="0%" stopColor="#fd9055" stopOpacity="1" />
            <Stop offset="30%" stopColor="#fdae57" stopOpacity="1" />
            <Stop offset="60%" stopColor="#fee0ab" stopOpacity="1" />
            <Stop offset="100%" stopColor="#ffffff" stopOpacity="1" />
          </RadialGradient>
        </Defs>
        <Rect x="0" y="0" width="100%" height="100%" fill="url(#grad)" />
      </Svg>

      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={styles.title}>R E M E T R A</Text>
        </View>

        <View style={styles.content}>
          <Text style={styles.question}>
            What are you hoping to accomplish with Remetra?
          </Text>
          <Text style={styles.subtitle}>Select all that apply</Text>

          <View style={styles.optionsContainer}>
            {GOAL_OPTIONS.map((goal) => (
              <TouchableOpacity
                key={goal}
                style={[
                  styles.optionButton,
                  selectedGoals.includes(goal) && styles.optionButtonSelected,
                ]}
                onPress={() => toggleGoal(goal)}
                activeOpacity={0.7}
              >
                <Text style={styles.optionText}>{goal}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity 
            style={styles.doneButton}
            onPress={handleDone}
          >
            <Text style={styles.doneText}>Done</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: '300',
    fontFamily: 'Lora_400Regular',
    letterSpacing: 3,
    color: '#eea487',
  },
  content: {
    flex: 1,
  },
  question: {
    fontSize: 18,
    color: '#C85A4A',
    fontFamily: 'PTSerif_400Regular',
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: '400',
  },
  subtitle: {
    fontSize: 14,
    color: '#C85A4A',
    fontFamily: 'PTSerif_400Regular',
    textAlign: 'center',
    marginBottom: 32,
    opacity: 0.8,
  },
  optionsContainer: {
    gap: 16,
    marginBottom: 40,
  },
  optionButton: {
    backgroundColor: '#D9806E',
    paddingVertical: 20,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  optionButtonSelected: {
    backgroundColor: '#B8624F',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  optionText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontFamily: 'PTSerif_400Regular',
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 20,
  },
  doneButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 16,
    borderRadius: 25,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
    marginTop: 'auto',
  },
  doneText: {
    color: '#C85A4A',
    fontFamily: 'PTSerif_400Regular',
    fontSize: 16,
    fontWeight: '600',
  },
});