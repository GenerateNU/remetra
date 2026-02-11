import { StyleSheet } from 'react-native';
import Svg, { Defs, RadialGradient, Stop, Rect } from 'react-native-svg';

export function BackgroundGradient () {

  return   (    
    <Svg height="100%" width="100%" style={StyleSheet.absoluteFill}>
      <Defs>
        <RadialGradient id="grad" cx="50%" cy="100%" r="80%">
          <Stop offset="0%" stopColor="#fd9055" stopOpacity="1" />
          <Stop offset="30%" stopColor="#fdae57" stopOpacity="1" />
          <Stop offset="60%" stopColor="#fee0ab" stopOpacity="1" />
          <Stop offset="80%" stopColor="#ffffff" stopOpacity="1" />
        </RadialGradient>
      </Defs>
      <Rect x="0" y="0" width="100%" height="100%" fill="url(#grad)" />
    </Svg>
  )
}