import { ReactNode, useEffect, useState } from 'react';
import { Animated, Text, View } from 'react-native';
import { Avatar28 } from './icons';

const BUBBLE_TEXT = 'font-figtree text-[14px] leading-5 text-remetra-text-primary';

export function UserBubble({ text }: { text: string }) {
  return (
    <View className="w-full flex-row justify-end">
      <View className="w-[260px] rounded-[24px] rounded-br-[8px] bg-remetra-canvas px-4 py-3">
        <Text className={BUBBLE_TEXT}>{text}</Text>
      </View>
    </View>
  );
}

function AssistantRow({ children }: { children: ReactNode }) {
  return (
    <View className="flex-row items-end gap-3">
      <Avatar28 width={28} height={28} />
      <View className="w-[260px] rounded-[24px] rounded-bl-[8px] border border-remetra-line-subtle bg-white px-4 py-3">
        {children}
      </View>
    </View>
  );
}

export function AssistantBubble({ text }: { text: string }) {
  return (
    <AssistantRow>
      <Text className={BUBBLE_TEXT}>{text}</Text>
    </AssistantRow>
  );
}

function TypingDot({ delay }: { delay: number }) {
  const [opacity] = useState(() => new Animated.Value(0.3));

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.delay(delay),
        Animated.timing(opacity, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.3, duration: 300, useNativeDriver: true }),
        Animated.delay(600 - delay),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [delay, opacity]);

  return <Animated.View style={{ opacity }} className="h-1.5 w-1.5 rounded-full bg-remetra-text-tertiary" />;
}

export function TypingBubble() {
  return (
    <View accessibilityLabel="Remetra is typing" className="flex-row items-end gap-3">
      <Avatar28 width={28} height={28} />
      <View className="flex-row items-center gap-1 rounded-[24px] rounded-bl-[8px] border border-remetra-line-subtle bg-white px-4 py-[19px]">
        <TypingDot delay={0} />
        <TypingDot delay={200} />
        <TypingDot delay={400} />
      </View>
    </View>
  );
}

/** Cards and follow-up chips sit under the bubble text, past the 28px avatar and 12px gap. */
export function Attachment({ children }: { children: ReactNode }) {
  return <View className="w-full pl-10">{children}</View>;
}
