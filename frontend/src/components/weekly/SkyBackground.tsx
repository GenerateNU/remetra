import { StyleSheet } from 'react-native';
import Svg, { Defs, LinearGradient, RadialGradient, Rect, Stop } from 'react-native-svg';

// Figma "Sky" (Remetra Design, node 7195:3924): a 393x240 band behind the top of the screen, stretched to fit.
const WIDTH = 393;
const HEIGHT = 240;

/** A peach fade from the top, with a golden glow in the top-right corner. */
export function SkyBackground() {
  return (
    <Svg
      width="100%"
      height={HEIGHT}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      preserveAspectRatio="none"
      style={styles.sky}
      pointerEvents="none"
    >
      <Defs>
        <LinearGradient id="skyFade" x1="0" y1="0" x2="0" y2={HEIGHT} gradientUnits="userSpaceOnUse">
          <Stop offset="0" stopColor="#fce6c4" />
          <Stop offset="0.55" stopColor="#fef2e0" stopOpacity={0.8} />
          <Stop offset="1" stopColor="#fef2e0" stopOpacity={0} />
        </LinearGradient>
        <RadialGradient
          id="skyGlow"
          cx="0"
          cy="0"
          r="10"
          gradientUnits="userSpaceOnUse"
          gradientTransform="matrix(21.615 0 0 13.2 306.54 28.8)"
        >
          <Stop offset="0" stopColor="#ffd98a" stopOpacity={0.9} />
          <Stop offset="0.4" stopColor="#ffd98a" stopOpacity={0.35} />
          <Stop offset="1" stopColor="#ffd98a" stopOpacity={0} />
        </RadialGradient>
      </Defs>
      <Rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="url(#skyFade)" />
      <Rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="url(#skyGlow)" />
    </Svg>
  );
}

const styles = StyleSheet.create({
  sky: { position: 'absolute', top: 0, left: 0, right: 0 },
});
