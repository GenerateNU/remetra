import { LinearGradient } from 'expo-linear-gradient';

/** Peach gradient behind the top of Remetra v22 screens. */
export function DawnWash() {
  return (
    <LinearGradient
      colors={['#fdddcc', '#fef0e7', '#faf8f6']}
      locations={[0, 0.5, 1]}
      style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 340 }}
      pointerEvents="none"
    />
  );
}
