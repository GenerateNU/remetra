import { View, Text, StyleSheet, TouchableOpacity, Dimensions, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import { useAppNavigation } from '../../navigation/hooks';

const { height } = Dimensions.get('window');

const GOAL_OPTIONS = [
  'Track symptoms related to autoimmune disease',
  'Identify trigger ingredients',
  'Discover correlations between current habits',
  'Improve quality of life through informed changes',
];

export function UserGoalsScreen() {
  const navigation = useAppNavigation();
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const toggleGoal = (goal: string) => {
    if (selectedGoals.includes(goal)) {
      setSelectedGoals(selectedGoals.filter(g => g !== goal));
    } else {
      setSelectedGoals([...selectedGoals, goal]);
    }
  };

  const handleDone = () => {
    navigation.navigate('finalboardingscreen?'); 
  };

  return (
    <LinearGradient
      colors={['#FFE5D9', '#FFB8A3', '#FFA78A', '#FF9A6C']}
      style={styles.container}
      locations={[0, 0.4, 0.7, 1]}
    >
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
    </LinearGradient>
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
    letterSpacing: 8,
    color: '#E8B4A0',
  },
  content: {
    flex: 1,
  },
  question: {
    fontSize: 18,
    color: '#C85A4A',
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: '400',
  },
  subtitle: {
    fontSize: 14,
    color: '#C85A4A',
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
    fontSize: 16,
    fontWeight: '600',
  },
});