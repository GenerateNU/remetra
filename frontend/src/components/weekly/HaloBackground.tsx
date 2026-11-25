import { StyleSheet } from 'react-native';
import Svg, { Defs, RadialGradient, Rect, Stop } from 'react-native-svg';

/** Figma "gradient/halo": a warm glow behind the top of the Insights screen. */
export function HaloBackground() {
  return (
    <Svg width="100%" height={420} style={styles.halo} pointerEvents="none">
      <Defs>
        <RadialGradient id="halo" cx="50%" cy="-30%" rx="110%" ry="130%" fx="50%" fy="-30%">
          <Stop offset="0" stopColor="#f7a35c" stopOpacity={0.55} />
          <Stop offset="0.55" stopColor="#ffe3a6" stopOpacity={0.3} />
          <Stop offset="1" stopColor="#ffe3a6" stopOpacity={0} />
        </RadialGradient>
      </Defs>
      <Rect x="0" y="0" width="100%" height="100%" fill="url(#halo)" />
    </Svg>
  );
}

const styles = StyleSheet.create({
  halo: { position: 'absolute', top: 0, left: 0, right: 0 },
});
