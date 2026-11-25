import Svg, { Circle, Defs, LinearGradient, RadialGradient, Stop } from 'react-native-svg';

const SIZE = 84;
const CENTER = SIZE / 2;
const STROKE = 5.88;
const RADIUS = CENTER - STROKE / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * Figma "Bloom ring": the sun inside a ring that fills as food groups are checked. Drawn from the Figma asset's
 * shapes and colors, with the progress arc computed from `progress` (0 to 1) instead of the mockup's fixed arc.
 */
export function BloomRing({ progress }: { progress: number }) {
  const clamped = Math.min(1, Math.max(0, progress));
  return (
    <Svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} testID="bloom-ring">
      <Defs>
        <RadialGradient id="bloomHalo" cx={CENTER} cy={CENTER} r={32} gradientUnits="userSpaceOnUse">
          <Stop offset="0" stopColor="#F7A35C" stopOpacity={0.55} />
          <Stop offset="0.55" stopColor="#FFE3A6" stopOpacity={0.3} />
          <Stop offset="1" stopColor="#FFE3A6" stopOpacity={0} />
        </RadialGradient>
        <LinearGradient id="bloomSun" x1={CENTER} y1={25} x2={CENTER} y2={59} gradientUnits="userSpaceOnUse">
          <Stop offset="0" stopColor="#FFE3A6" />
          <Stop offset="0.5" stopColor="#F7A35C" />
          <Stop offset="1" stopColor="#F26A5B" />
        </LinearGradient>
      </Defs>
      <Circle cx={CENTER} cy={CENTER} r={RADIUS} stroke="#F4F0EC" strokeWidth={STROKE} fill="none" />
      {clamped > 0 && (
        <Circle
          testID="bloom-ring-progress"
          cx={CENTER}
          cy={CENTER}
          r={RADIUS}
          stroke="#2A1F1A"
          strokeWidth={STROKE}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={`${CIRCUMFERENCE * clamped} ${CIRCUMFERENCE}`}
          transform={`rotate(-90 ${CENTER} ${CENTER})`}
        />
      )}
      <Circle cx={CENTER} cy={CENTER} r={32} fill="url(#bloomHalo)" />
      <Circle cx={CENTER} cy={CENTER} r={17} fill="url(#bloomSun)" />
    </Svg>
  );
}
