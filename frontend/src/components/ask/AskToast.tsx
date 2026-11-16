import { useEffect, useState } from 'react';
import { Animated, Text } from 'react-native';
import { CheckWhiteIcon } from './icons';

const VISIBLE_MS = 2400;

export function AskToast({ message, top, onDismiss }: { message: string; top: number; onDismiss: () => void }) {
  const [opacity] = useState(() => new Animated.Value(0));

  useEffect(() => {
    const animation = Animated.sequence([
      Animated.timing(opacity, { toValue: 1, duration: 180, useNativeDriver: true }),
      Animated.delay(VISIBLE_MS),
      Animated.timing(opacity, { toValue: 0, duration: 220, useNativeDriver: true }),
    ]);
    animation.start(({ finished }) => finished && onDismiss());
    return () => animation.stop();
  }, [message, onDismiss, opacity]);

  return (
    <Animated.View
      accessibilityLiveRegion="polite"
      pointerEvents="none"
      className="absolute flex-row items-center gap-2 self-center rounded-full bg-remetra-text-primary px-4 py-2.5"
      style={{
        top,
        opacity,
        shadowColor: '#3B2924',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 20,
        elevation: 6,
      }}
    >
      <CheckWhiteIcon width={16} height={16} />
      <Text className="font-figtree-semibold text-[13px] text-white">{message}</Text>
    </Animated.View>
  );
}
